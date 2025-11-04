# The App Backend

Installing The App backend using both **Poetry** and **Python virtual environments (venv)**.

---

## Prerequisites

- Python 3.10 or higher
- Git (optional, if you want to clone the repo)

---

## Setup

You can use either **Poetry** or **venv** to manage dependencies and run the project.

---

### 1. Using Poetry

Poetry is a tool for dependency management and packaging in Python.

1. **Install Poetry** if you don't have it:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Clone the repository**:
```bash
git clone https://github.com/highlander0302/The_app-backend
cd The_app_backend
```

3. **Install dependencies**:
```bash
poetry install
```

4. **Activate the virtual environment**:
```bash
poetry env activate
```
then copy and past the url interminal to activate the env

5. **Apply database migrations**:
```bash
python manage.py migrate
```

6. **Run the development server**:
```bash
python manage.py runserver
```

7. Open your browser and go to `http://127.0.0.1:8000/` to see the app.

---

### 2. Using venv (Python Virtual Environment)

1. **Clone the repository**:
```bash
git clone https://github.com/highlander0302/The_app-backend
cd The_app-backend
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - On macOS/Linux:
```bash
   source venv/bin/activate
```
   - On Windows:
```bash
   venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Apply database migrations**:
```bash
python manage.py migrate
```

6. **Run the development server**:
```bash
python manage.py runserver
```

7. Open your browser and go to `http://127.0.0.1:8000/` to see the app.

---
