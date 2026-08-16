"""Name who holds the card right now, and refuse a second stage beside them.

Lifted out of `run_experiment.py`. It exists because of one afternoon: on
2026-08-16 the grid was launched three times and killed twice inside seventeen
minutes, by a session and by that session's own subagent, neither able to see
the other. Two separate failures, and this file addresses both, one by refusing
the overlap and one by writing the owner where anyone reaching for a `pkill`
will look.
"""

import contextlib
import datetime
import json
import os
import pathlib

OWNER = pathlib.Path(__file__).parent / "results" / ".running"


class AlreadyRunning(RuntimeError):
    """Another stage owns the card. Two at once is how the log got raced."""


def _session_name():
    """Something a person or another agent can act on.

    A marker that says "ask the owner" and then reads `unknown session` is half
    a mechanism: the session next door had to find the owner from a chat message
    instead of from the file. The variable is CLAUDE_CODE_SESSION_ID, not
    CLAUDE_SESSION_ID, which is why the first version was always empty.
    """
    session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    return f"claude session {session}" if session else f"pid {os.getppid()} (no session id)"


def _owner_is_alive(owner):
    try:
        os.kill(int(owner["pid"]), 0)
    except (OSError, ValueError, KeyError):
        return False
    return True


def read_owner(marker=OWNER):
    """Who is running a stage right now, or None."""
    if not marker.exists():
        return None
    try:
        owner = json.loads(marker.read_text())
    except json.JSONDecodeError:
        return None
    return owner if _owner_is_alive(owner) else None


@contextlib.contextmanager
def owning_the_run(stage, marker=OWNER):
    """Claim the run, and say on disk and on screen who holds it.

    It refuses a second launch while one is live, which is the overlap that
    produced the race. And it names the owner where anyone reaching for a
    `pkill` will look, because the agent that killed this was right that
    something hot needed stopping and wrong that it could decide alone.
    """
    live = read_owner(marker)
    if live is not None:
        raise AlreadyRunning(
            f"stage {live.get('stage')} is already running as PID {live['pid']}, "
            f"started {live.get('started')} by {live.get('owner')}. "
            f"Wait for it, or ask its owner to stop it. Do not kill it blind.")
    marker.parent.mkdir(exist_ok=True)
    marker.write_text(json.dumps({
        "pid": os.getpid(), "stage": stage,
        "started": datetime.datetime.now().isoformat(timespec="seconds"),
        "owner": _session_name(),
        "note": "ask the owner before killing this; it holds the GPU for ~an hour",
    }, indent=2) + "\n")
    print(f"owner: PID {os.getpid()} holds stage {stage}. "
          f"{marker} names it; ask before killing.")
    try:
        yield
    finally:
        marker.unlink(missing_ok=True)
