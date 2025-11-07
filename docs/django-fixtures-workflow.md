# Django JSON Fixtures Workflow

This document explains how to export, share, and update database data using JSON fixtures (`db_data.json`) in a Django project.

## 1️⃣ Exporting Database Data

After populating your database with seed or test data:

### Export All Data
```bash
python manage.py dumpdata --indent 2 > db_data.json
```

- Exports all apps and tables into `db_data.json`.
- `--indent 2` formats JSON for readability.

### Export Specific App(s)
```bash
python manage.py dumpdata myapp --indent 2 > db_data.json
```

- Only exports models from `myapp`.
- Useful to avoid dumping Django system tables like `auth` or `sessions`.

### Commit JSON File
```bash
git add db_data.json
git commit -m "Update db_data.json with latest data"
git push origin main
```

- Makes the data available to other developers via your repository.

## 2️⃣ Importing Data from JSON

When pulling updated JSON from the repository:

### Step 1: Pull Latest Repository Changes
```bash
git pull origin main
```

### Step 2: Apply Migrations
```bash
python manage.py migrate
```

- Ensures the database schema matches the models before loading data.

### Step 3: Load JSON Data
```bash
python manage.py loaddata db_data.json
```

- Populates the database with data from the JSON file.
- Existing entries with matching primary keys may be overwritten.

### Step 4: Verify

Open Django shell or admin to confirm data is present:
```bash
python manage.py shell
```
```python
from myapp.models import MyModel
print(MyModel.objects.all())
```

## 3️⃣ Workflow When Changing Models

When you modify models in your application:

### 1. Create and Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Regenerate JSON Fixture
```bash
python manage.py dumpdata myapp --indent 2 > db_data.json
```

- Ensures the fixture reflects the updated schema and data.

### 3. Commit Updated JSON
```bash
git add db_data.json
git commit -m "Update db_data.json after model changes"
git push origin main
```

### 4. Teammates Workflow

Pull latest changes:
```bash
git pull origin main
python manage.py migrate
python manage.py loaddata db_data.json
```

## 4️⃣ Best Practices

### Separate Schema vs Data

- Migrations (`makemigrations`) manage schema.
- Fixtures (`db_data.json`) manage data only.

### Update JSON After Data Changes

- Keeps the file in sync with the current database state.

### Always Migrate First

- Never load JSON into a database with mismatched schema.

### Limit Scope If Needed

Dump only your app data to avoid including unnecessary system tables:
```bash
python manage.py dumpdata myapp --indent 2 > db_data.json
```

## ✅ Summary Workflow Table

| Action | Command |
|--------|---------|
| Export data | `python manage.py dumpdata myapp --indent 2 > db_data.json` |
| Commit JSON | `git add db_data.json && git commit -m "Update data"` |
| Pull JSON | `git pull origin main` |
| Apply migrations | `python manage.py migrate` |
| Load data | `python manage.py loaddata db_data.json` |
| After model changes | Migrate → regenerate JSON → commit → teammates pull → migrate → loaddata |

---

This ensures a consistent and reproducible way for teams to share database content while keeping schema and data synchronized.
