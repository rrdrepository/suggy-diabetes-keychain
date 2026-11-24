# Shared data format: `data/state.json`

Both apps (the keychain and the companion app, which a parent looks after) share **one JSON file**:
`data/state.json`. There is no server, no account and no internet.
Each app re-reads the file about once per second, so a change made in one
window shows up in the other.

This document is the "contract". If you add or rename a key, update this
file first, then update `DEFAULT_STATE` in `state_store.py`.

## Rules

1. Only the helper module `state_store.py` reads or writes the file.
   Screens never open the file directly.
2. Always **read, change, then write straight away** (the helper's
   `update_state()` does this for you). This way one app does not wipe out
   what the other app just saved.
3. Each app only changes the keys it owns (see the "Written by" column).
4. If the file is missing, empty or half-written, the helper does not crash.
   It uses the last good copy it read, or the default values below.
5. Times are text in ISO format, for example `"2026-11-21T12:30:00"`.
   Dates are `"YYYY-MM-DD"`.

## Keys

| Key | Type | Example | Written by | Meaning |
|---|---|---|---|---|
| `version` | number | `1` | helper | Format version. Lets us change the format later. |
| `updated_at` | text or null | `"2026-11-21T12:30:00"` | helper | When the file was last saved. |
| `keychain_ref` | text | `"KC-4821"` | keychain | The reference number printed on this keychain. The app checks it when linking. |
| `link.linked` | true/false | `true` | app | Has a parent linked this keychain in the app? |
| `link.linked_at` | text or null | `"2026-11-21T10:00:00"` | app | When it was linked. |
| `link.nickname` | text or null | `"Radin"` | app | Typed in the app (max 8 letters). The keychain greets "Hello Radin!". |
| `pet.mood` | text | `"happy"` | keychain | Always `"happy"` for now. |
| `pet.awake` | true/false | `true` | keychain | `false` while Suggy is asleep (0 hearts). Waking Suggy up on the keychain sets it back to `true` with full hearts. |
| `pet.hearts` | number 0 to 5 | `4` | keychain | Life span hearts. A feeding with pretend sugar 8.0 or more takes 1 away, other feedings give 1 back. |
| `pet.accessories` | list | `["cap", "sunglasses"]` | app | The cosmetics Suggy is **wearing** now (at most one from each shop category). Drawn on the keychain and in the app. |
| `pet.owned` | list | `["cap", "crown", "sunglasses"]` | app | Every cosmetic bought in the shop. Kept when Suggy falls asleep. |
| `pet.last_meal` | object or null | see below | keychain | The most recent feeding and Suggy's pretend sugar level. |
| `pet.everyday_foods_eaten` | number | `5` | keychain | Count of light ("everyday") foods fed so far. |
| `pet.sometimes_foods_eaten` | number | `1` | keychain | Count of sweet ("sometimes") foods fed so far. |
| `insulin.gap_minutes` | number 0 to 30 | `15` | app | Minutes between insulin and eating, from the doctor's plan. Used for the "Eat in 15 min" countdown. |
| `insulin.reminders` | list of 4 | see below | app | The reminder times a parent set. There is **no dose** anywhere. |
| `insulin.log` | list | see below | keychain | What the kid pressed OK on (newest last, up to 60). |
| `points.balance` | number | `40` | both | Points the kid can spend (with a parent). The keychain adds points, the shop takes them away. |
| `points.earned_total` | number | `120` | both | All points ever earned. |
| `feed_log` | list | see below | keychain | Every finished feeding (newest last, up to 50). Each item looks like `pet.last_meal`. |
| `vouchers` | list | see below | app | Demo vouchers claimed with points (newest last). Each has `id`, `kind`, `title`, `note`, `cost`, `code` and `claimed_at`. The codes are made up. |
| `quiz.date` | text or null | `"2026-11-21"` | app | The day the quiz answers below are for. |
| `quiz.answers` | list | `[{"id": "who_sugar", "pick": 0, "correct": true}]` | app | Today's quiz answers so far (up to 5). |
| `kid_quiz.points_date` | text or null | `"2026-11-22"` | keychain | The day the kids' quiz last gave points, so only the first round of a day gives points. |
| `glucose_logs` | list | see below | app (planned) | Readings **typed in by hand**. Never measured by the device. Not used by the keychain any more. |
| `risk_result` | object or null | see below | app | Last questionnaire result. Not a diagnosis. |

### One item in `glucose_logs`

| Key | Type | Example | Meaning |
|---|---|---|---|
| `value_mmol` | number | `5.6` | Always in mmol/L, with 1 decimal place. Allowed range 1.0 to 50.0. |
| `context` | text | `"fasting"` | One of `"fasting"` (shown as "Before food"), `"after_meal_2h"` ("After a meal"), `"random"` ("Other time"). Required. |
| `logged_at` | text | `"2026-11-21T07:45:00"` | When it was logged. |
| `source` | text | `"app"` | Where it was typed in. |
| `demo` | true/false | `true` | `true` for the made-up demo data used in the 30-day chart. |

The keychain does not show or add readings (it has feeding, the insulin reminder and Check only).

### `insulin.reminders` and `insulin.log`

Each reminder: `id`, `label`, `time` ("HH:MM", 24-hour), `on` (true when
a parent switched it on) and `with_meal` (true when a meal follows).

Each log row: `reminder` (the id, or `"demo"`), `label`, `date`, `due`
(the planned time, null for the demo), `with_meal`, `insulin_at` (when
OK was pressed on "Insulin time!"), `ate_at` (when OK was pressed on
"I ate", null until then) and `demo` (true when it came from the demo
button).

### `pet.last_meal`

| Key | Type | Example | Meaning |
|---|---|---|---|
| `foods` | list | `["brown_rice", "water", "apple"]` | The three food ids picked (the food list is in `keychain/feeding.py`). |
| `sweet_picks` | number 0 to 3 | `0` | How many of the three picks were the sweet food. Decides Suggy's face: 0 smile, 1 flat mouth, 2 or 3 frown. |
| `food_names` | list | `["Brown rice", "Water", "Apple"]` | The names of the three foods, for the app's list. |
| `points` | number | `30` | Points this feeding gave: 10 for each light choice. |
| `pretend_sugar` | number | `6.4` | Suggy's **pretend** sugar level, a game number for the pet only. It is not anyone's real glucose. 5.0 plus the made-up rise of each food. |
| `at` | text | `"2026-11-21T12:10:00"` | When the pet ate. |
| `hearts_change` | number | `1` | `+1` or `-1`: what this feeding did to Suggy's hearts. |
| `fell_asleep` | true | `true` | Only present if this meal took the last heart (Suggy fell asleep). |

### `risk_result`

| Key | Type | Example | Meaning |
|---|---|---|---|
| `level` | text | `"Moderate"` | One of `"Low"`, `"Moderate"`, `"High"`. |
| `answered_at` | text | `"2026-11-21T09:10:00"` | When the questionnaire was done. |

Only the level is saved, not the individual answers.

## Privacy note

- The IC number is **never** stored in this file (or anywhere). The app
  only checks that it looks like a real IC, then forgets it. No age group is kept.
- When the keychain is not linked, the file holds only the pet, insulin
  reminder, points and feeding keys. No personal data.
- Demo only: use made-up IC numbers.

## Full example file

```json
{
  "version": 1,
  "updated_at": "2026-11-21T12:30:00",
  "keychain_ref": "KC-4821",
  "link": {
    "linked": true,
    "linked_at": "2026-11-21T10:00:00"
  },
  "pet": {
    "mood": "happy",
    "awake": true,
    "hearts": 5,
    "accessories": ["cap"],
    "owned": ["cap", "crown"],
    "last_meal": {
      "foods": ["brown_rice", "water", "apple"],
      "food_names": ["Brown rice", "Water", "Apple"],
      "sweet_picks": 0,
      "points": 30,
      "pretend_sugar": 6.4,
      "at": "2026-11-21T12:10:00",
      "hearts_change": 1
    },
    "everyday_foods_eaten": 3,
    "sometimes_foods_eaten": 0
  },
  "insulin": {
    "gap_minutes": 15,
    "reminders": [
      {"id": "breakfast", "label": "Breakfast", "time": "07:00", "on": true, "with_meal": true},
      {"id": "lunch", "label": "Lunch", "time": "12:30", "on": true, "with_meal": true},
      {"id": "dinner", "label": "Dinner", "time": "19:00", "on": false, "with_meal": true},
      {"id": "bedtime", "label": "Bedtime", "time": "21:30", "on": false, "with_meal": false}
    ],
    "log": [
      {"reminder": "lunch", "label": "Lunch", "date": "2026-11-22", "due": "12:30", "with_meal": true,
       "insulin_at": "2026-11-22T12:33:00", "ate_at": "2026-11-22T12:47:00", "demo": false}
    ]
  },
  "points": {
    "balance": 40,
    "earned_total": 40
  },
  "feed_log": [
    {
      "foods": ["brown_rice", "water", "apple"],
      "food_names": ["Brown rice", "Water", "Apple"],
      "sweet_picks": 0,
      "points": 30,
      "pretend_sugar": 6.4,
      "at": "2026-11-21T12:10:00",
      "hearts_change": 1
    }
  ],
  "vouchers": [
    {
      "id": "brown_rice",
      "kind": "Food swaps",
      "title": "RM5 off brown rice",
      "note": "instead of white rice",
      "cost": 100,
      "code": "DEMO-7KQ2-XM4P",
      "claimed_at": "2026-11-21T13:00:00"
    }
  ],
  "quiz": {
    "date": "2026-11-21",
    "answers": [
      {"id": "who_sugar", "pick": 0, "correct": true}
    ]
  },
  "glucose_logs": [
    {
      "value_mmol": 5.4,
      "context": "fasting",
      "logged_at": "2026-11-20T07:30:00",
      "demo": true
    },
    {
      "value_mmol": 7.1,
      "context": "after_meal_2h",
      "logged_at": "2026-11-21T14:05:00",
      "demo": false
    }
  ],
  "risk_result": {
    "level": "Moderate",
    "answered_at": "2026-11-21T09:10:00"
  }
}
```
