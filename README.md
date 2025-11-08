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

### 3. Activate the virtual environment
```bash
poetry env activate
```

you will see something like this:
```bash
source /home/your_root_dir/some_folder/the_app-backend/.venv/bin/activate
```
Copy and paste the line in your terminal to activate the env. If you see `(the-app-backend-py3.12)` prefixing your terminal line, the env is activated.
```bash
>>>(the-app-backend-py3.12)<<< ➤ your_root_dir@your_admin_name-your_computer_model ~/some_dir/the_app-backend $
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Run the development server
```bash
python manage.py runserver
```

### 6. Access the application
Open your browser and go to `http://localhost:5173` to interact with the backend from the React frontend,
or `http://127.0.0.1:8000/admin/` to see the app admin panel (backend).

---

# Now when you've done with the project you can install and configure the database.

---

# PostgreSQL Setup & Environment Variables
The backend uses PostgreSQL as the database. Each developer should create their own local database and `.env` file.

## 1. Install PostgreSQL
* **Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

* **macOS (using Homebrew):**

```bash
brew install postgresql
brew services start postgresql
```
* **Windows:** Download and install from [PostgreSQL official site](https://www.postgresql.org/download/windows/).

## 2. Create a Database and User
Open the PostgreSQL shell:

```bash
psql -U postgres
```

Then create a database and user for the project:

```sql
CREATE DATABASE ecommerce_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO your_username;
\q
```

Replace `ecommerce_db`, `your_username`, and `your_password` with your own preferred values.

## 3. Create a `.env` File
In the project root, at the same level as `manage.py`, create a `.env` file containing the database credentials:

```
POSTGRES_DB=ecommerce_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

**Important:** The `.env` file must remain at the same level as `manage.py`, otherwise the backend will not be able to read the database credentials. Make sure this file is never committed to Git. Add it to `.gitignore` if not already included.

## 4. Populate the Database (Optional)
If you want to use sample data:

```bash
python manage.py loaddata db_data.json
```

## 5. Run the Backend
Activate your Poetry environment and run the server:

```bash
python manage.py migrate
python manage.py runserver
```

Your backend will now connect to your local PostgreSQL database using the credentials in the `.env` file.
