#!/usr/bin/env bash
# One-shot setup: install deps, create tables, load demo data.
set -e
python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python manage.py makemigrations accounts skills students opportunities applications notifications
python manage.py migrate
python manage.py seed_data
echo "Done. Start the server with: python manage.py runserver"
