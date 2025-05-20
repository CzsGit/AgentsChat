# AgentsChat

AgentsChat is a simple group chat system where human users can interact with each other and with pluggable agents. The project contains a FastAPI backend and a very small HTML/JS frontend. The backend keeps data in memory for simplicity.

## Running the backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API listens on `http://localhost:8000` by default.

## Frontend

Open `frontend/index.html` in a browser. The page provides a minimal interface for login and chatting.

This is only a demonstration implementation and does not persist data. The code is structured so that it can be extended with a proper database and richer frontend later.

## Features
- Multi-user login and registration
- Admin endpoints for managing agents and users
- Group chat where members and agents can post messages
- Agents are triggered when mentioned with `@name`
- Users can add friends and create or join multiple groups
- Messages can contain text or uploaded audio files

This repository is intentionally minimal. It provides a starting point for further development of a full people-and-agent group chat system.
