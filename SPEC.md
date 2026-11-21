# Study Session Tracker — Creative Project Plan

Megha Patel · IS218-001 · Review 1: Plan

Status: AI-assisted planning draft. The research documentation exists; the application, human review, GitHub publication, and runtime checks are pending. The student should review and own these proposed choices before submission.

## Question and audience

How can a small Python application save a student's completed study sessions securely and make their study time easy to understand?

The primary audience is a college student recording completed study sessions. An alternative audience is a tutor tracking several students. I propose the individual student because it avoids shared permissions and keeps one complete workflow manageable. The assumption that students prefer manual entry still needs a real peer's feedback.

## Two concepts and decision

| Concept | Useful interaction and saved record | Benefit | Cost or boundary |
| --- | --- | --- | --- |
| Study Session Tracker | Enter a completed session and view private totals | Clear numeric outcomes and a small workflow | Requires honest manual entry; does not measure learning |
| Internship Application Tracker | Save applications and update their statuses | Supports an internship search | Adds application editing and status rules; no employer integration |

Proposed choice: Study Session Tracker. Both can support accounts and saved records, but the study tracker has fewer workflow states. The tradeoff is that recorded minutes do not show whether a student understood a subject. No user research has established demand yet.

## Dream, promise, and experiment

Dream: A friendly study planner that helps students understand their habits across classes.

Promise: A student can register, sign in, record a completed study session, see that record after returning, view a private dashboard, sign out, and update their display name and password.

Creative experiment — planned: Compare a plain recent-session list with a list plus weekly progress summary. Keep the records and task the same. Ask a real peer to find total minutes and the latest session without coaching. Record accuracy and confusion; do not infer improved learning. Stop after one comparison and one revision. Fall back to the plain list if the summary makes the task harder.

AI experiment — planned: Ask AI to propose invalid duration cases, independently define expected results, inspect the suggestions, and later run those cases against the implementation. Predict that AI will help identify edge cases but may miss ownership rules. Record actual successes and errors after execution; no result is claimed now.

## Technical comparison and stack

| Approach | Fit | Tradeoff |
| --- | --- | --- |
| Flask server with SQLite | Fits Python experience and a small local application | Account security, ownership, validation, and deployment still require work |
| Browser-only JavaScript with local storage | Easy static prototype | Does not establish server-side account protection or the required private persisted workflow |

Proposed stack: Python, Flask, Flask-Login for session management, Werkzeug password hashing, Flask-WTF for form/CSRF support, SQLite, HTML/CSS, pytest, and Playwright browser checks. Exact compatible dependency versions will be selected and checked during implementation. Flask-Login alone does not implement registration, password management, or record-level permissions.

The two research sites are static documentation. The later study application needs a running backend; GitHub Pages cannot run that Python backend.

## Five stories and acceptance checks

| ID | Story | Planned success check | Planned failure check |
| --- | --- | --- | --- |
| S1 | As a student, I want to register, sign in, and sign out so I can access my work. | A valid synthetic account can sign in; sign-out blocks private pages. | Duplicate account and incorrect password show useful errors without exposing secrets. |
| S2 | As a student, I want to record a completed session so I can track time by subject. | A valid subject, date, and integer duration create one record. | Blank subject, future date, non-integer duration, and minutes outside 1–1440 create no record. |
| S3 | As a student, I want my sessions saved so I can return later. | The record remains after a new session and application restart using the same database. | A failed submission leaves the saved records unchanged. |
| S4 | As a student, I want a private dashboard so I can review my recent work. | Show only my records, session count, and total minutes; an empty account has guidance. | Another account cannot obtain my records through pages or direct requests. |
| S5 | As a student, I want to update my account so it stays current. | Change my display name; change my password after supplying the current password, then require sign-in again. | Wrong current password or an attempt to modify another account is rejected. |

Validation limits are proposed product rules, not conclusions from the technical sources. Subject: 1–80 trimmed characters. Note: optional, at most 240 characters. Date: valid calendar date, no later than the server's current date. Records use synthetic data while testing. Historical timezone handling remains a documented design question before implementation.

## Data and architecture

| Part | Responsibility |
| --- | --- |
| Browser | Accessible forms, field errors, dashboard, and empty state |
| Flask routes | Validate requests, authenticate sessions, enforce record ownership, coordinate responses |
| Study service | Validate session values and calculate totals |
| Repository functions | Parameterized database queries and transaction boundaries |
| SQLite | Persist users and sessions on disk |

Users: id, unique account identifier, display_name, password_hash, created_at. Study sessions: id, user_id, subject, session_date, duration_minutes, optional note, created_at. A session belongs to exactly one user. The server derives user_id from the authenticated session rather than trusting a submitted owner ID.

Architecture sketch: browser → Flask routes → study service → repository → SQLite. Authentication/session support protects routes; ownership checks protect each record. See the diagram on the research page.

Use password hashes rather than plaintext passwords, parameterized SQL, CSRF protection for state changes, and configuration outside source control. Use synthetic accounts. These are implementation commitments and need actual verification later.

## Pattern experiment — planned

Problem: validation and totals could become mixed into routes. Compare direct route/database code with a small service and repository boundary. Use the same valid and invalid fixtures for both. Compare clarity, duplicate rules, test isolation, and added indirection. Keep the boundary only if its benefit is explainable; avoid a generic framework or unnecessary classes. Neither approach has been implemented or tested yet.

## Research evidence

Sources reviewed with AI-assisted retrieval on November 11, 2026. Megha's own source walkthrough remains pending.

| Original source | Observed evidence | Decision or planned check |
| --- | --- | --- |
| [Flask tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) | Its example includes registration, login, user-owned posts, database structure, and testing. | Use a structured server application; adapt concepts rather than present the tutorial as my code. |
| [Flask-Login documentation](https://flask-login.readthedocs.io/en/latest/) | It handles sessions and logged-in access; it does not provide registration or record permissions. | Plan explicit registration, password workflows, and owner-filtered queries. |
| [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html) | SQLite supports disk-backed storage, commits, and bound query parameters. | Check save/reopen persistence and use parameterized queries. |

Facts: these documents describe framework and storage capabilities. Interpretation: the proposed stack is suitable for this bounded project. Assumptions: students want manual entry, the workload fits available time, and a simple summary helps. No cited source establishes student demand or proves this application secure.

## Two presentation approaches

A: Calm single-column form with recent sessions underneath. B: Summary cards above the same form and records. Proposed starting point: A, because the primary action remains easy to locate. Both use labeled inputs, readable contrast, keyboard focus, and the same data. Peer comparison is planned, not observed.

First-screen sketch A: page title, short explanation, subject/date/minutes/note form, Save session button, recent sessions. Sketch B: page title, total/count summary, the identical form, recent sessions. These are layout proposals rather than running application controls.

## Checks, review, and next step

Observed: original technical documentation was retrieved; a planning record and static research page were prepared with AI assistance. Local document/HTML structure checks are recorded in CHECKS.md.

Not run: application tests, authentication tests, database persistence tests, browser usability/accessibility checks, GitHub Actions, and real peer review. There is no working study application yet.

Peer task: Open a technical source, explain the stack choice, and identify one assumption or confusing part. Reviewer/date/revision: pending. Issue/change/verification/retry links: pending. Use PEER-REVIEW.md; do not close an issue before the actual resolution and retry.

Next: Review these choices, publish the documentation, complete a real peer walkthrough, and then implement the account/core-task first slice for the later review.

## AI assistance and limits

ChatGPT helped research original documentation, draft the plan, create the static page, and propose checks. AI did not interview students or run the future application. Megha must review source claims and explain the selected design. The chosen idea and proposed limits are draft decisions until she reviews them. Expectation: faster organization; observed result: draft documentation and source comparisons; next time: define independent expected results before asking AI to suggest tests.


## Review 2 — First working slice — November 20, 2026

Implemented in the prepared source: Flask registration/sign-in/sign-out, server-owned study entry, SQLite storage, record reopening, minimal private list and totals. Exact test evidence and limits: [CHECKS.md](CHECKS.md). Pattern trial: [PATTERN-EXPERIMENT.md](PATTERN-EXPERIMENT.md). Run instructions: [README.md](README.md). The research site remains index.html. The local application starts with python app.py after dependency installation. Account display-name/password maintenance remains future work. This update supersedes historical statements that no application exists. Code/tests were generated and executed with ChatGPT; student explanation and real peer retry are not established.
