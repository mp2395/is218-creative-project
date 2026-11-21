# Review 2 — Repository boundary versus direct function

Problem: authenticated-owner filtering could be duplicated across route handlers.

Tried code: tracker/storage.py StudyRepository.get_owned versus pattern_experiment.py simple_get_owned. Both query by record ID AND authenticated user ID. Same SQLite fixture and independently specified expected values are used in tests/test_tracker.py::test_repository_and_simpler_alternative_match_independent_expectations.

Observed: both return IS218/45 minutes for owner 1, None for owner 2, and None for a missing record. The experiment is included in the 38 passing checks.

Decision: retain the small repository because add, recent, and get_owned share the storage boundary and routes remain readable. Cost: a class and indirection. The function is shorter and is a reasonable choice for one lookup. This experiment establishes equivalent scoped behavior for these fixtures, not a speed or security advantage from classes. The fallback function remains as runnable comparison code. Validation stays a plain function; no generic repository framework was added.

AI expectation/result: ChatGPT generated the trial and tests. A class alone does not solve authorization; the owner condition and authenticated identity do. Student review and real peer task remain pending.
