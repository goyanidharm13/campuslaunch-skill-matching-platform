@echo off
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
python manage.py makemigrations accounts skills students opportunities applications notifications
python manage.py migrate
python manage.py seed_data
echo Done. Start the server with: python manage.py runserver
