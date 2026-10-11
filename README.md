# CampusLaunch

Student Skills & Career Opportunity Platform: Python, Django, MySQL, Django REST Framework, HTML/CSS/JavaScript.

## Quick start
```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
./setup.sh                                          # Windows: setup.bat
python manage.py runserver
```
`setup.sh` installs requirements, creates migrations, migrates and runs `seed_data`.
The default database is SQLite so it runs with zero setup. For MySQL 8, create a database
(`CREATE DATABASE campuslaunch CHARACTER SET utf8mb4;`), then set `DB_ENGINE=mysql` and the `DB_*` values in `.env`
before running `setup.sh`.

## Demo logins (created by `python manage.py seed_data`)
| Role | Username | Password |
| --- | --- | --- |
| Admin | admin | Admin@123 |
| Student | aarav (also diya, rohan, isha, kabir, meera, neel, sara) | Campus@123 |
| Recruiter | recruiter_technova (also recruiter_cloudspark, recruiter_edubridge) | Campus@123 |

`seed_data` is idempotent; `seed_data --reset` wipes demo data first. Aarav matches "Django Intern" at 92% (11/12 weight,
Docker missing) and "Cloud Backend Associate" at 67% (missing Docker, AWS), the same examples as the slides.

## Project layout (module order as in the deck)
`accounts` auth and roles | `students` profile, education, projects, certifications | `skills` catalog and student skills |
`opportunities` posts, filters, search | `applications` apply and status | `matching` score, gap, recommendations |
`recruiter` dashboard and ranking | `notifications` alerts | `api` REST endpoints | `config` settings and URLs |
`templates/`, `static/css`, `static/js`.

## REST API (session or basic auth)
`GET /api/opportunities/` and `/<id>/` | `GET /api/skills/` | `GET /api/recommended/` | `GET, POST /api/applications/` |
`GET, PUT /api/profile/` | `GET /api/matching/<id>/` | `GET /api/skill-gap/<id>/` | `GET /api/notifications/`
Opportunity list filters: `?q=&type=&location=&remote=true&deadline_before=&deadline_after=&relevant=true`

## Tests and scheduled job
```bash
pytest
python manage.py send_deadline_alerts --days 3     # run daily via cron / Task Scheduler
```
Set `DEBUG=False`, a strong `SECRET_KEY` and real `ALLOWED_HOSTS` in `.env` for production.

## Forgot password
Log in page -> "Forgot password?" -> enter email -> reset link -> choose new password.
In development the email prints in the terminal running `runserver` (find the line starting with `http://127.0.0.1:8000/accounts/reset/...`).
For real email set the `EMAIL_*` values in `.env` (example in `.env.example`). Links expire after 1 hour, work once,
never reveal whether an email has an account, and are limited to 5 requests per hour per IP.
