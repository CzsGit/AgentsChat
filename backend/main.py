from __future__ import annotations

import os
from datetime import datetime
from typing import List
from uuid import uuid4

import requests
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import auth
from .models import Agent, Group, Message, User
from .store import store

app = FastAPI(title="AgentsChat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if any(u.username == username for u in store.users.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(id=str(uuid4()), username=username, password_hash=auth.hash_password(password))
    store.add_user(user)
    token = auth.create_token(user.id)
    return {"token": token}


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    for user in store.users.values():
        if user.username == username and user.password_hash == auth.hash_password(password):
            token = auth.create_token(user.id)
            return {"token": token}
    raise HTTPException(status_code=400, detail="Invalid credentials")


@app.get("/me")
def me(user: User = Depends(auth.get_current_user)):
    return user


# User management (admin)
@app.get("/users")
def list_users(user: User = Depends(auth.get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return list(store.users.values())


@app.delete("/users/{user_id}")
def delete_user(user_id: str, user: User = Depends(auth.get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    store.users.pop(user_id, None)
    return {"status": "deleted"}


# Agent management (admin)
@app.post("/agents")
def create_agent(name: str = Form(...), description: str = Form(""), api_url: str = Form(""), user: User = Depends(auth.get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    agent = Agent(id=str(uuid4()), name=name, description=description, api_url=api_url)
    store.add_agent(agent)
    return agent


@app.get("/agents")
def list_agents(user: User = Depends(auth.get_current_user)):
    return list(store.agents.values())


@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str, user: User = Depends(auth.get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    store.agents.pop(agent_id, None)
    return {"status": "deleted"}


# Group management
@app.post("/groups")
def create_group(name: str = Form(...), user: User = Depends(auth.get_current_user)):
    group = Group(id=str(uuid4()), name=name, owner_id=user.id, members={user.id})
    store.add_group(group)
    user.groups.add(group.id)
    return group


@app.post("/groups/{group_id}/join")
def join_group(group_id: str, user: User = Depends(auth.get_current_user)):
    group = store.groups.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    group.members.add(user.id)
    user.groups.add(group_id)
    return {"status": "joined"}


@app.get("/groups/{group_id}/messages")
def get_messages(group_id: str, user: User = Depends(auth.get_current_user)):
    group = store.groups.get(group_id)
    if not group or user.id not in group.members:
        raise HTTPException(status_code=403, detail="Not a member")
    return [m for m in store.messages.values() if m.group_id == group_id]


@app.post("/groups/{group_id}/messages")
def post_message(
    group_id: str,
    content: str = Form(""),
    file: UploadFile | None = File(None),
    user: User = Depends(auth.get_current_user),
):
    group = store.groups.get(group_id)
    if not group or user.id not in group.members:
        raise HTTPException(status_code=403, detail="Not a member")
    msg_type = "text"
    audio_path = None
    if file:
        msg_type = "audio"
        audio_path = os.path.join(UPLOAD_DIR, f"{uuid4()}_{file.filename}")
        with open(audio_path, "wb") as f:
            f.write(file.file.read())
    message = Message(id=str(uuid4()), group_id=group_id, sender_id=user.id, content=content, timestamp=datetime.utcnow(), type=msg_type, audio_path=audio_path)
    store.add_message(message)
    # call agent if '@name' present
    for agent_id in group.agents:
        agent = store.agents[agent_id]
        pattern = f"@{agent.name}"
        if pattern in content:
            try:
                resp = requests.post(agent.api_url, json={"message": content})
                if resp.ok:
                    agent_reply = Message(
                        id=str(uuid4()),
                        group_id=group_id,
                        sender_id=agent_id,
                        content=resp.text,
                        timestamp=datetime.utcnow(),
                    )
                    store.add_message(agent_reply)
            except Exception:
                pass
    return message


@app.post("/friends/{friend_id}")
def add_friend(friend_id: str, user: User = Depends(auth.get_current_user)):
    if friend_id not in store.users:
        raise HTTPException(status_code=404, detail="Friend not found")
    user.friends.add(friend_id)
    return {"status": "added"}


@app.get("/groups")
def my_groups(user: User = Depends(auth.get_current_user)):
    return [store.groups[g] for g in user.groups if g in store.groups]


@app.post("/groups/{group_id}/agents/{agent_id}")
def add_agent_to_group(group_id: str, agent_id: str, user: User = Depends(auth.get_current_user)):
    group = store.groups.get(group_id)
    if not group or group.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only owner can add agents")
    if agent_id not in store.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    group.agents.add(agent_id)
    return {"status": "added"}
