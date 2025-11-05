# The App Backend

Installing The App backend using **Python virtual environments (venv)**.

---

## Prerequisites

- Python 3.10 or higher
- Git (optional, if you want to clone the repo)

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/highlander0302/The_app-backend
cd The_app-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

> **Note:** On some systems, you may need to use `python3` instead of `python`.

### 3. Activate the virtual environment

- **On Windows:**
```bash
  venv\Scripts\activate
```

- **On macOS/Linux:**
```bash
  source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Access the application

Open your browser and go to `http://127.0.0.1:8000/` to see the app.

---

## Deactivating the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment by running:
```bash
deactivate
```

This works the same way on Windows, macOS, and Linux.
