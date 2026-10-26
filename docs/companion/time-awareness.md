# Companion time awareness

Each real companion turn receives local processing time, user-message arrival time,
the previous user turn's stored time, elapsed seconds and local-date crossing.
The clock is scoped to the current transcript, excludes subagents and group chats,
and stays out of the cached system prompt and visible text. New conversations and
legacy messages with missing timestamps have unknown gaps; no activity is inferred.
An explicitly configured HoneyOS timezone wins; otherwise companion time uses
Asia/Shanghai to avoid a proot host's accidental UTC. Other runtime clocks retain
their existing defaults. Configure `timezone: Asia/Shanghai` in config.yaml for
consistent scheduler timezone as well.

The model decides whether the gap matters using prior conversation, current input,
relationship and boundaries. No mandatory time announcements, duration-based scripts,
guessing activities, claims of continuous background waiting, or guilt about absence.
Warmth and expressions of missing someone are allowed when context supports them;
they are never required by a duration threshold. These are instructions, not a
proof that every stochastic model response will obey them.

UI displays stored message times and date separators in the same timezone. Unknown
legacy times remain blank. Live user times start as device timestamps and reconcile
with the server's run-start event; assistant completion uses the server event time.
The original text and credentials remain unchanged.

Verification: `python -m unittest discover -s tests/companion -p test_time_context.py`;
inside frontend: `npm test` and `npm run build`. The committed react_dist build lets
the phone pull this update without installing Node or rebuilding the frontend.
