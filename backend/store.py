"""In-memory data store."""
from __future__ import annotations

from typing import Dict
from uuid import uuid4

from .models import Agent, Group, Message, User


class DataStore:
    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.agents: Dict[str, Agent] = {}
        self.messages: Dict[str, Message] = {}
        self.tokens: Dict[str, str] = {}  # token -> user_id

    def add_user(self, user: User) -> None:
        self.users[user.id] = user

    def add_agent(self, agent: Agent) -> None:
        self.agents[agent.id] = agent

    def add_group(self, group: Group) -> None:
        self.groups[group.id] = group

    def add_message(self, message: Message) -> None:
        self.messages[message.id] = message


store = DataStore()
