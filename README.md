# The App Backend

## Prerequisites
- Docker Engine
- Docker compose v2

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/highlander0302/The_app-backend
cd The_app-backend
```

### 2. Create .env file
```bash
cp .env.example .env
```
**Important:** The `.env` file must remain at the same level as `manage.py`, otherwise the backend will not be able to read the database credentials. Make sure this file is never committed to Git. Add it to `.gitignore` if not already included.

### 3. Build and start the app in background
This command will build an image for Django app and start Django container as well as PostgreSQL container
```bash
docker compose up -d
```
**Please note that existing Python environment directories(like .venv) will be mounted to the container.** 
**It may affect dependencies resolution.**

### 4. Access the application
Open your browser and go to `http://localhost:5173` to interact with the backend from the React frontend,
or `http://127.0.0.1:8000/admin/` to see the app admin panel (backend).

## Docker compose commands

### 1. Stop and remove containers and volumes
```bash
docker compose down -v
```

### 2. Build the project
```bash
docker compose build
```
**You can add `--no-cache` flag to rebuild without using previously cached steps**
