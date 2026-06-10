# TeachAndLearn

A web platform connecting private teachers with students in Belgium.
Built with Django + HTMX, deployed on Hostinger VPS.

---

## Project Goal

Allow teachers offering private lessons to create a profile and be discovered by students looking for tutoring. Initial focus is language lessons, but the data model must support any subject category.

---

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Django templates + HTMX (no separate JS framework)
- **CSS:** TailwindCSS
- **Database:** PostgreSQL
- **Auth:** Django built-in auth (email + password, no social login)
- **Maps:** OpenStreetMap + Nominatim API (geocoding, no Google Maps)
- **Deployment:** Hostinger VPS, gunicorn + nginx

---

## Core Features

### User Roles
- A user can be a **teacher**, a **student**, or **both**
- Role is set at registration and can be updated in profile settings
- A teacher role must be validated y the Admin before being published and it requires ID validation.

### Registration & Auth
- Sign up with email + password
- Email verification before accessing the platform
- Login / logout
- Password reset via email

### Teacher Profile
- Bio
- Subject(s) taught (e.g. French, English — linked to a Subject model, not hardcoded)
- Native language
- Price per hour (€)
- Availability (free text for now)
- Municipality (public) and full address (private, used for map display only)
- Certificates / credentials (name, issuing org, date obtained, expiry, optional file upload)
- Average rating (computed from reviews)
- Validation state: `draft` → `validated` or `rejected` by admin

### Student Profile
- Bio
- Subject(s) they want to learn
- Proficiency level per subject (beginner / elementary / intermediate / upper-intermediate / advanced / native)
- Learning goals (free text)
- Municipality

### Teacher Directory (public search)
- Only validated teachers are listed
- Filter by: subject, municipality, max price per hour
- Sort by rating (default)
- Requires login to view full profiles and contact teachers

### Teacher Detail Page
- Full profile with avatar, bio, subjects, price, availability
- Location map (OSM embed, approximate — municipality level)
- Reviews with star ratings
- Contact button (opens a message thread)

### Messaging
- Students initiate contact with a teacher
- Conversation thread per student-teacher pair
- States: `new` → `ongoing` → `closed`
- Both parties can send messages within a thread

### Reviews
- Students can leave one review per teacher (1–5 stars + comment)
- A student cannot review themselves
- Only students can write reviews
- Reviews are validated before being published: `draft` → `validated` or `rejected` by admin

### Admin
- Django admin panel
- Validate or reject teacher profiles
- Manage subjects (add/remove)
- View all users, conversations, and reviews

---

## Data Model Overview

- **User** — extends Django AbstractUser, login by email
- **Profile** — one per user; holds role flags, bio, municipality, address
- **Subject** — name (e.g. "French", "Mathematics"); generic, not language-specific
- **TeacherProfile** — linked to Profile; subjects, price, availability, state, certificates
- **StudentProfile** — linked to Profile; subjects, level, learning goals
- **Certificate** — linked to TeacherProfile; name, org, dates, optional file
- **Review** — student → teacher; rating + comment; unique per pair
- **Conversation** — student + teacher pair; state
- **Message** — belongs to Conversation; sender + body + timestamp

---

## Design Principles

- Keep it simple: no JavaScript framework, HTMX for dynamic interactions
- Subject is a FK/M2M, never a hardcoded choice list — allows expansion without code changes
- Address is private; only municipality is shown publicly
- Mobile-friendly (Tailwind responsive classes)
- Belgian context: default currency EUR, French/Dutch/German subject names expected
- The website is adapted for desktop and smartphone views

---

## Out of Scope (for now)

- Online payments
- Video lessons integration
- Social login (Google, Facebook)
- Native mobile app
- Multi-language UI (French/Dutch/German) — English UI first

---

## Deployment Notes

- Target: Hostinger VPS
- Stack: gunicorn + nginx + PostgreSQL
- Static files: served by nginx
- Media files (certificate uploads): stored locally, served by nginx
- Environment variables for secrets (SECRET_KEY, DB credentials, email config)

