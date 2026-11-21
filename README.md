# Study Session Tracker — Review 2

Megha Patel / IS218. Local first working slice generated with ChatGPT; student walkthrough and real peer review remain pending.

## Start on a Mac

Open Terminal inside this repository folder, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5051. Create a synthetic account with a 12-character-or-longer password, sign in, save IS218 / 45 minutes / a past date, sign out, stop with Control+C, restart with python app.py, sign in, and reopen the saved record from My sessions. Do not submit the password or database to GitHub.

## Automated checks

```bash
python -m pytest -q
```

38 checks were executed during preparation. See CHECKS.md and evidence/pytest.txt. They include a new app instance using the same database. Run again on your Mac and record your own results.

## Architecture and limits

Browser -> Flask routes and Flask-Login -> validation / StudyRepository -> SQLite. CSRFProtect guards POST requests. Werkzeug hashes passwords. Queries bind SQL parameters and filter by the authenticated owner. SQLite and a generated secret are kept under instance/, ignored by Git. Synthetic testing only.

This is a local class prototype. No rate limiting, recovery/email service, multi-session revocation, or production deployment is claimed. Public hosting requires HTTPS, secure-cookie configuration, operational hardening, and review. Display-name/password maintenance is planned for later. GitHub Pages serves index.html research documentation; it cannot run app.py.

Date handling uses the server's local calendar date for completed sessions. Timezone-aware history is future work. No database migration is needed for this first schema; later schema changes need an explicit migration.

Research: index.html. Same evolving project record: SPEC.md. Pattern comparison: PATTERN-EXPERIMENT.md. Real peer task: REVIEW-TASK.md.
