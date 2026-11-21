"""Business rules independent of Flask and storage."""
from datetime import date


def validate_study(data, *, today):
    subject = data.get('subject', '').strip()
    note = data.get('note', '').strip()
    raw_minutes = data.get('duration_minutes', '').strip()
    if not 1 <= len(subject) <= 80:
        raise ValueError('Enter a subject of 1–80 characters.')
    if not raw_minutes.isascii() or not raw_minutes.isdecimal() or len(raw_minutes) > 4:
        raise ValueError('Enter whole minutes from 1 to 1440.')
    minutes = int(raw_minutes)
    if not 1 <= minutes <= 1440:
        raise ValueError('Enter whole minutes from 1 to 1440.')
    raw_date = data.get('session_date', '')
    try:
        day = date.fromisoformat(raw_date)
    except ValueError:
        raise ValueError('Enter a valid study date.') from None
    if day.isoformat() != raw_date or day > today:
        raise ValueError('Enter a date on or before today.')
    if len(note) > 240:
        raise ValueError('Keep the note to 240 characters or fewer.')
    return subject, day.isoformat(), minutes, note
