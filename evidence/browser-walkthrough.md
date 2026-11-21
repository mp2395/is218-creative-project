# Observed browser walkthrough — November 20, 2026

Performed by ChatGPT through the browser against the local prepared Flask app, not by Ana or a real peer.

1. Opened registration; created synthetic browser_review_1 account.
2. Signed in; observed 0 minutes / 0 sessions and useful empty-state text.
3. Saved IS218 Browser Review, 45 minutes, date 2026-11-20, with a synthetic note.
4. Observed saved record #1 and exact field values.
5. Signed out; observed public welcome page.
6. Stopped and restarted the actual preview server using the same SQLite file.
7. Signed in again; observed 45 minutes / 1 session.
8. Reopened record #1 and verified subject, date, minutes, and note unchanged.

Result: PASS for this browser path. Test database and credentials are not included in the deliverable. The pytest suite separately exercises negative inputs, CSRF, passwords, and cross-account reads. Student Mac run and real peer feedback/retry remain pending.
