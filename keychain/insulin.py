"""
insulin.py - the rules of the insulin reminder (no drawing here).

How it works:
- A parent sets the reminder times in the companion app, copied from
  the doctor's plan. Every kid's plan is different, so nothing is fixed
  in the code. The times are saved in data/state.json under "insulin".
- When a time comes, the keychain shows "Insulin time!". The kid
  presses OK after taking it, and we save the time.
- If that insulin goes with a meal, the keychain then counts down
  ("Eat in 15 min"). The kid presses OK after eating, and we save that
  time too. The app shows both times, so a parent or doctor can see
  the gap between insulin and food.

IMPORTANT: there is NO dose anywhere. The keychain only reminds about
the TIME. It never says how much insulin to take, and it gives no
advice. This is a prototype, not a medical device.
"""

import datetime

import state_store

# The pretend reminder shown by the "Insulin reminder now" demo button
# under the keychain. Its log rows are marked "demo".
DEMO_REMINDER = {"id": "demo", "label": "Demo", "time": None,
                 "with_meal": True, "demo": True}

# A reminder keeps showing for this long after its time. After that we
# stop asking (the kid is not nagged all day).
REMIND_FOR_MINUTES = 120


def _today_at(time_text):
    """Today's date with the clock time "HH:MM" (None if it is not a time)."""
    parsed = state_store.parse_time(time_text)
    if parsed is None:
        return None
    return datetime.datetime.combine(datetime.date.today(),
                                     datetime.time(parsed[0], parsed[1]))


def _from_text(iso_text):
    """Saved time text -> a datetime (None if it can't be read)."""
    try:
        return datetime.datetime.fromisoformat(iso_text)
    except (ValueError, TypeError):
        return None


def todays_entry(state, reminder_id):
    """The log row for this reminder today (None if not pressed yet)."""
    today = state_store.today_text()
    for entry in state["insulin"]["log"]:
        if (entry.get("reminder") == reminder_id
                and entry.get("date") == today and not entry.get("demo")):
            return entry
    return None


def todays_reminders(state):
    """
    The reminders that are switched on, earliest first, each with a
    status for today:
        "done"   the kid pressed OK
        "now"    it is time (the reminder is showing or will show)
        "later"  its time has not come yet
        "past"   its time passed more than 2 hours ago with no press
    Returns a list of (reminder, status).
    """
    now = datetime.datetime.now()
    rows = []
    for reminder in state["insulin"]["reminders"]:
        due = _today_at(reminder.get("time"))
        if not reminder.get("on") or due is None:
            continue
        if todays_entry(state, reminder.get("id")):
            status = "done"
        elif now < due:
            status = "later"
        elif now < due + datetime.timedelta(minutes=REMIND_FOR_MINUTES):
            status = "now"
        else:
            status = "past"
        rows.append((due, reminder, status))
    rows.sort(key=lambda row: row[0])
    return [(reminder, status) for _due, reminder, status in rows]


def due_reminder(state):
    """
    The reminder that should be on the screen right now, or None.
    """
    for reminder, status in todays_reminders(state):
        if status == "now":
            return reminder
    return None


def log_insulin(state, reminder):
    """
    The kid pressed OK on "Insulin time!": save when (changes the state
    in place). Returns the new log row.
    """
    entry = {
        "reminder": reminder.get("id"),
        "label": reminder.get("label"),
        "date": state_store.today_text(),
        "due": reminder.get("time"),          # the planned time, "HH:MM"
        "with_meal": bool(reminder.get("with_meal")),
        "insulin_at": state_store.now_text(),  # when OK was pressed
        "ate_at": None,                        # filled in by log_ate()
        "demo": bool(reminder.get("demo")),    # True = from the demo button
    }
    log = state["insulin"]["log"]
    log.append(entry)
    del log[:-state_store.KEEP_INSULIN_LOGS]     # keep the newest only
    return entry


def waiting_to_eat(state):
    """
    The newest log row where insulin was taken with a meal and the kid
    has not pressed "I ate" yet (None if there is none). Rows older
    than 2 hours are left alone.
    """
    now = datetime.datetime.now()
    for entry in reversed(state["insulin"]["log"]):
        taken = _from_text(entry.get("insulin_at"))
        if taken is None or not entry.get("with_meal") or entry.get("ate_at"):
            continue
        if now - taken < datetime.timedelta(minutes=REMIND_FOR_MINUTES):
            return entry
    return None


def seconds_until_meal(state, entry):
    """Seconds left before it is time to eat (0 when the time has come)."""
    taken = _from_text(entry.get("insulin_at"))
    if taken is None:
        return 0
    eat_time = taken + datetime.timedelta(
        minutes=state["insulin"]["gap_minutes"])
    return max(0, int((eat_time - datetime.datetime.now()).total_seconds()))


def log_ate(state):
    """The kid pressed OK on "I ate": save when (changes the state in place)."""
    entry = waiting_to_eat(state)
    if entry is not None:
        entry["ate_at"] = state_store.now_text()
