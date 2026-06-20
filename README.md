# my_ecommerce

Simple Django e-commerce sample project.

## Quick start

- Create and activate a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run migrations and start dev server:

```bash
python manage.py migrate
python manage.py runserver
```

## Notes

- The repository ignores `venv/`, `.venv/`, `database/`, `db.sqlite3`, and `media/` (see `.gitignore`).
- Do not store production database files in the repo.