from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    username: str
    password_hash: str
    is_admin: bool = False
    friends: Set[str] = Field(default_factory=set)
    groups: Set[str] = Field(default_factory=set)
    openai_key: Optional[str] = None


class Agent(BaseModel):
    id: str
    name: str
    description: str
    api_url: str


class Group(BaseModel):
    id: str
    name: str
    owner_id: str
    members: Set[str] = Field(default_factory=set)
    agents: Set[str] = Field(default_factory=set)


class Message(BaseModel):
    id: str
    group_id: str
    sender_id: str
    content: str
    timestamp: datetime
    type: str = "text"  # text or audio
    audio_path: Optional[str] = None
