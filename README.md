# The App Backend
Installing The App backend using **Poetry**.

---

## Prerequisites
- Python 3.10 or higher
- Poetry ([Installation guide](https://python-poetry.org/docs/#installation))
- Git

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/highlander0302/The_app-backend
cd The_app-backend
```

### 2. Install dependencies
Poetry will automatically create a virtual environment and install all dependencies from the lock file:
```bash
poetry install
```

### 3. Apply database migrations
```bash
poetry run python manage.py migrate
```

### 4. Run the development server
```bash
poetry run python manage.py runserver
```

### 5. Access the application
Open your browser and go to `http://localhost:5173` to interact with the backend from the React frontend,
or `http://127.0.0.1:8000/admin/` to see the app admin panel (backend).

---

## Working with Poetry

### Activate the virtual environment
If you prefer to work inside an activated shell (instead of prefixing commands with `poetry run`):
```bash
poetry env activate
```

you will see something like this:
```bash
source /home/yourrootdir/somefolder/the_app-backend/.venv/bin/activate
```
Copy and pase this line in your teminal to activate the env.
```bash
*(the-app-backend-py3.12)* ➤ your_root_dir@your_admin_name-your_computer_model ~/some_dir/the_app-backend $
```

Then you can run commands directly:
```bash
python manage.py runserver
```

### Exit the Poetry
```bash
exit
```

---
