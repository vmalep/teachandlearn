# TeachAndLearn

A web platform connecting private teachers with students in Belgium.

> 🚧 This project is currently under active development.

**Live:** [teachandlearn.cloud](https://teachandlearn.cloud)

---

## What is TeachAndLearn?

TeachAndLearn allows private teachers to create a profile and be discovered by students looking for tutoring. Teachers can list the subjects they teach, their price, availability, and credentials. Students can browse validated teacher profiles, read reviews, and get in touch directly through the platform.

The initial focus is language lessons, but the platform supports any subject category.

---

## Features

### For teachers
- Create a public profile with bio, subjects, price per hour, availability and certificates
- Profile must be validated by an admin before appearing in the directory
- Receive and display student reviews (after admin validation)
- Private address stored for map display; only municipality shown publicly

### For students
- Browse and filter the teacher directory (by subject, municipality, price)
- View teacher profiles with ratings and location map
- Contact teachers via an integrated messaging thread
- Leave a review after interacting with a teacher

### For both
- Dual role: a user can be both a teacher and a student
- Multilingual interface: English, French, Dutch, German, Spanish, Russian
- Mobile-friendly responsive design

### Admin
- Validate or reject teacher profiles and reviews via the Django admin panel
- Manage subjects, users, and conversations

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 (Python 3.12) |
| Frontend | Django templates + HTMX |
| CSS | Tailwind CSS v4 |
| Database | PostgreSQL |
| Auth | Django built-in (email + password) |
| Maps | Leaflet + CARTO tiles, Nominatim geocoding |
| Deployment | Gunicorn + Nginx on Hostinger VPS |

---

## Project Structure

```
config/          Django settings and root URLs
accounts/        Custom user model, registration, email verification
profiles/        Base profile (location, avatar, bio, roles)
teachers/        Teacher profile, certificates, directory
students/        Student profile, subjects and levels
subjects/        Subject model (generic, not hardcoded)
reviews/         Student reviews with admin validation
messaging/       Conversation threads and messages
locale/          Translation files (fr, nl, de, es, ru)
templates/       All HTML templates
static/          CSS (Tailwind input + compiled output)
```

---

## Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL
- [Tailwind CSS standalone CLI](https://tailwindcss.com/blog/standalone-cli) (placed at `bin/tailwindcss`)

### Setup

```bash
git clone https://github.com/vmalep/teachandlearn.git
cd teachandlearn

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create a .env file (see .env.example)
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### CSS (watch mode)
```bash
./bin/tailwindcss -i static/css/input.css -o static/css/main.css --watch
```

### Translations
```bash
python manage.py makemessages -l fr  # generate/update .po files
# edit locale/fr/LC_MESSAGES/django.po
python manage.py compilemessages     # compile to .mo
```

---

## Deployment

The project is deployed on a Hostinger VPS (Ubuntu 22.04) with gunicorn + nginx.

```bash
ssh deploy@<server-ip> "cd /home/deploy/app && bash scripts/deploy.sh"
```

The deploy script runs: `git pull` → Tailwind build → `collectstatic` → `migrate` → restart gunicorn.

---

## Data Model

```
User (email login)
└── Profile (bio, location, avatar, roles)
    ├── TeacherProfile (subjects, price, availability, state, certificates)
    └── StudentProfile (subjects + levels, learning goals)

Subject (generic — French, Mathematics, etc.)
Review (student → teacher, rating + comment, admin-validated)
Conversation (student ↔ teacher thread)
└── Message (body, sender, timestamp)
```

Teacher profiles and reviews go through an admin validation workflow:
`draft` → `validated` (published) or `rejected` (with reason)

---

## Roadmap

- [ ] Complete multilingual translations
- [ ] Teacher profile ID validation flow
- [ ] Student–teacher booking / scheduling
- [ ] Email notifications for messages and reviews
- [ ] URL-prefix i18n (`/fr/`, `/nl/`, …) for SEO

---

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).

In short: you can use, modify, and distribute this software freely, but any modified version — including one run as a web service — must also be released under AGPL v3.
