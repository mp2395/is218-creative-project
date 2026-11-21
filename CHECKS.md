# Review 2 check record — November 20, 2026

## Observed during AI-assisted preparation

- Python 3.12; dependencies pinned in requirements.txt.
- Command: python -m pytest -q. Result: 38 passed. Exact output: [evidence/pytest.txt](evidence/pytest.txt).
- Rule checks: subject/note/date/minute boundaries; invalid inputs create no rows.
- Account/data checks: duplicate account, password hashing, invalid credentials, CSRF, signed-out pages, logout method, owner filtering, forged submitted owner ignored, escaped text, bound SQL, rollback after a simulated failed write, no-store headers.
- Restart check: a new application instance using the same SQLite file can sign in and reopen the previously saved record.
- Pattern check: same fixture, owner/wrong-owner/missing-record expectations for repository and simple lookup function.
- Actual browser registration/sign-in/save/sign-out/server-restart/sign-in/reopen: PASS. See [browser walkthrough](evidence/browser-walkthrough.md). Browser screenshots were inspected for readable saved-record layout.
- Static research HTML: local link and fragment structure checked.

## Not run / limits

Student Mac walkthrough, real peer task/retry, production hosting and security review, phone browser check, broad accessibility audit, and CI execution are not claimed. Account maintenance remains later work. Test success does not prove the app secure or production-ready. Source/research changes must still be uploaded to the existing GitHub repository and live links rechecked. This record supersedes old Review 1 pending-implementation statements.

AI: ChatGPT generated code, tests, trial, and documentation and performed these preparation checks. Megha still needs to review and explain the implementation.

 Student Mac verification — November 20, 2026:
- Ran python -m pytest -q: 38 passed in 4.36 seconds.
- Created an account, signed in, and saved an IS218 session for 45 minutes.
- Signed out, stopped and restarted the app, signed in again, and reopened record #1.
- The subject, date, duration, and note remained unchanged.