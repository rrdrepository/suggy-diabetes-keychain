"""
state_store.py - the ONLY code that reads and writes data/state.json.

Both apps keep an identical copy of this file:
    keychain/state_store.py
    adult-app/state_store.py
If you change one, copy it over the other so they stay the same.
(We use two copies so each app runs with a plain `python main.py`
without any import path tricks.)

The keys are described in docs/data-format.md.

How to use it from other code:

    import state_store

    state = state_store.load_state()          # read (never crashes)

    def take_a_heart(state):                  # change something...
        state["pet"]["hearts"] -= 1

    state_store.update_state(take_a_heart)    # ...read, change, save
"""

import copy
import datetime
import json
import os
import time

# ---------------------------------------------------------------------------
# Where the file lives.
# This file sits in keychain/ or adult-app/, so the project folder is one
# level up, and the data file is <project>/data/state.json.
# Using __file__ means it works no matter which folder you run from.
# ---------------------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
STATE_PATH = os.path.join(DATA_DIR, "state.json")

FORMAT_VERSION = 1

# This demo keychain's reference number (as if printed on the device).
KEYCHAIN_REF = "KC-4821"

# ---------------------------------------------------------------------------
# Default values, used when the file is missing or a key is missing.
# Must match docs/data-format.md.
# ---------------------------------------------------------------------------
DEFAULT_STATE = {
    "version": FORMAT_VERSION,
    "updated_at": None,
    "keychain_ref": KEYCHAIN_REF,  # printed on the keychain
    "link": {                    # set by the companion app
        "linked": False,
        "linked_at": None,
        "nickname": None,        # typed in the app, shown as "Hello ..."
    },
    "pet": {
        "mood": "happy",         # always "happy" for now
        "awake": True,           # False while Suggy sleeps (0 hearts left)
        "hearts": 5,             # life span hearts, 0..5
        "accessories": [],       # cosmetics Suggy is WEARING now, e.g. ["cap"]
        "owned": [],             # every cosmetic bought in the app shop
        "last_meal": None,       # the last feeding: {foods, pretend_sugar, at, hearts_change}
        "everyday_foods_eaten": 0,
        "sometimes_foods_eaten": 0,
    },
    "insulin": {                 # the insulin reminder (see docs/flow.md)
        # The times are set by a parent in the app, copied from the
        # doctor's plan. There is NO dose anywhere, only times.
        "gap_minutes": 15,       # minutes between insulin and eating
        "reminders": [           # always these 4 rows; "on" switches one on
            {"id": "breakfast", "label": "Breakfast", "time": "07:00",
             "on": False, "with_meal": True},
            {"id": "lunch", "label": "Lunch", "time": "12:30",
             "on": False, "with_meal": True},
            {"id": "dinner", "label": "Dinner", "time": "19:00",
             "on": False, "with_meal": True},
            {"id": "bedtime", "label": "Bedtime", "time": "21:30",
             "on": False, "with_meal": False},
        ],
        "log": [],               # what the kid pressed OK on, oldest first
    },
    "points": {
        "balance": 0,            # points the user can spend in the shop
        "earned_total": 0,       # all points ever earned
    },
    "feed_log": [],              # every finished feeding, oldest first
    "vouchers": [],              # demo vouchers claimed in the app
    "quiz": {
        "date": None,            # day the answers below are for
        "answers": [],           # today's answers so far: list of {id, pick, correct}
    },
    "kid_quiz": {                # the kids' quiz on the keychain
        "points_date": None,     # the day its points were last given
    },
    "glucose_logs": [],          # list of {value_mmol, context, logged_at, source, demo}
    "risk_result": None,         # None or {level, answered_at}
}

# The last good state we read. If the file is half-written at the moment
# we read it, we return this instead of crashing or losing data.
_last_good_state = None


def now_text():
    """Current local time as text, e.g. '2026-11-21T12:30:00'."""
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def today_text():
    """Today's date as text, e.g. '2026-11-21'."""
    return datetime.date.today().isoformat()


def default_state():
    """A fresh copy of the defaults (a copy, so nobody edits the original)."""
    return copy.deepcopy(DEFAULT_STATE)


def _fill_missing_keys(loaded, defaults):
    """
    Start from the defaults and copy in whatever the file had.
    This way a file with a missing key (or a wrong type) still works.
    Goes one level deep into small dicts like "pet" and "points".
    """
    result = copy.deepcopy(defaults)
    if not isinstance(loaded, dict):
        return result
    for key, default_value in defaults.items():
        if key not in loaded:
            continue
        value = loaded[key]
        if isinstance(default_value, dict):
            # A nested group such as "pet": fill it key by key.
            if isinstance(value, dict):
                result[key] = _fill_missing_keys(value, default_value)
        elif isinstance(default_value, list):
            if isinstance(value, list):
                result[key] = value
        else:
            result[key] = value
    return result


def load_state():
    """
    Read data/state.json and return it as a Python dict.

    Never crashes:
    - file missing          -> default values
    - file empty or broken  -> last good copy (or defaults if none yet)
    """
    global _last_good_state

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except FileNotFoundError:
        return default_state()
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        # Half-written, empty or locked for a moment. Use what we had.
        if _last_good_state is not None:
            return copy.deepcopy(_last_good_state)
        return default_state()

    state = _fill_missing_keys(loaded, DEFAULT_STATE)
    _last_good_state = copy.deepcopy(state)
    return state


def save_state(state):
    """
    Save the whole state to data/state.json safely.

    We write to a temporary file first, then swap it in with os.replace().
    The swap is all-or-nothing, so the other app never sees half a file.
    """
    global _last_good_state

    os.makedirs(DATA_DIR, exist_ok=True)
    state["version"] = FORMAT_VERSION
    state["updated_at"] = now_text()

    # A temp file name unique to this app's process.
    temp_path = STATE_PATH + ".tmp" + str(os.getpid())
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    # On Windows the swap can fail for a split second if the other app is
    # reading the file right then. Try a few times before giving up.
    for attempt in range(10):
        try:
            os.replace(temp_path, STATE_PATH)
            break
        except PermissionError:
            time.sleep(0.05)
    else:
        # Could not swap: tidy up and report it, but don't crash the app.
        try:
            os.remove(temp_path)
        except OSError:
            pass
        print("state_store: could not save state.json, will try next time")
        return False

    _last_good_state = copy.deepcopy(state)
    return True


def update_state(change_function):
    """
    Read the newest state, let change_function edit it, then save.

    Always use this to make changes, so you don't overwrite something the
    other app saved a moment ago.

    change_function gets the state dict and edits it in place.
    Returns the new state.
    """
    state = load_state()
    change_function(state)
    save_state(state)
    return state


# ---------------------------------------------------------------------------
# Points. The user earns points and spends them in the app's shop.
#   +10 for each light food choice in a feeding (given by feeding.py)
#   +5 for each right answer in the app's daily quiz (given by quiz.py)
#   +5 for each right answer in the keychain's kids' quiz, for the first
#      round of the day only (given by kid_quiz.py)
# ---------------------------------------------------------------------------
POINTS_PER_REWARD = 10
KEEP_FEEDINGS = 50        # feedings to keep in the feed log
KEEP_INSULIN_LOGS = 60    # insulin log rows to keep


def add_points(state, amount):
    """Give the user some points (changes the state in place)."""
    state["points"]["balance"] += amount
    state["points"]["earned_total"] += amount


def parse_time(time_text):
    """
    Turn a clock time typed as text, like "07:00" or "7:05", into
    (hour, minute). Returns None if it is not a real time.
    """
    parts = str(time_text).strip().split(":")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        return None
    hour, minute = int(parts[0]), int(parts[1])
    if hour > 23 or minute > 59:
        return None
    return hour, minute


# ---------------------------------------------------------------------------
# Self-test: run `python state_store.py` to check the helper works.
# It uses a temporary folder, so your real data/state.json is not touched.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    test_dir = tempfile.mkdtemp()
    DATA_DIR = os.path.join(test_dir, "data")
    STATE_PATH = os.path.join(DATA_DIR, "state.json")

    # 1. Missing file -> defaults
    s = load_state()
    assert s["link"]["linked"] is False and s["pet"]["hearts"] == 5
    print("OK  missing file gives default values")

    # 2. Save and read back
    def link_it(state):
        state["link"]["linked"] = True
        state["link"]["nickname"] = "Aiman"
        state["pet"]["hearts"] = 3
    update_state(link_it)
    s = load_state()
    assert s["link"]["nickname"] == "Aiman" and s["pet"]["hearts"] == 3
    print("OK  save then load gives the same values")

    # 3. Half-written file -> last good copy, no crash
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write('{"link": {"linked": tr')
    s = load_state()
    assert s["link"]["nickname"] == "Aiman"
    print("OK  half-written file gives the last good copy")

    # 4. Missing keys -> filled from defaults
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        f.write('{"link": {"linked": true}}')
    s = load_state()
    assert s["link"]["linked"] is True and s["link"]["nickname"] is None
    assert s["pet"]["mood"] == "happy"
    print("OK  missing keys are filled in with defaults")

    # 5. Points add up
    add_points(s, 10)
    assert s["points"]["balance"] == 10 and s["points"]["earned_total"] == 10
    print("OK  points are added to the balance")

    # 6. The insulin reminder starts with 4 rows, all switched off
    assert len(s["insulin"]["reminders"]) == 4
    assert not any(r["on"] for r in s["insulin"]["reminders"])
    print("OK  insulin reminders start switched off")

    # 7. Clock times typed as text
    assert parse_time("07:30") == (7, 30) and parse_time("7:05") == (7, 5)
    assert parse_time("25:00") is None and parse_time("soon") is None
    print("OK  clock times are checked")

    print("All checks passed.")
