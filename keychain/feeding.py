"""
feeding.py - the feeding rules for Suggy (no drawing in here).

Rules (from the team's design):
- Suggy can be fed at any time, as often as the player likes.
- Every feeding goes step by step: MEAL, then DRINK, then DESSERT.
- Each step is a choice between TWO very different foods: a sweet one
  and a light one. There are several pairs for each step, and every
  feeding picks one pair at random, so the foods change each time.
- A short description under each food, in words a kid can read, so the
  player can compare them. No numbers and nothing scary.
- After the three steps, Suggy shows a PRETEND sugar level based on the
  choices. It is a game number for the pet only. It is not anyone's real
  glucose.
- Suggy has up to 5 hearts of life span. More sugar takes a heart away,
  lighter choices give one back. At 0 hearts Suggy is very tired and
  falls asleep. Waking Suggy up gives all the hearts back. Nothing is
  lost: the cosmetics and the points stay.
- Every light food choice earns the kid 10 points (so up to 30 points
  in one feeding). Points are spent on cosmetics in the app's shop.
- Every finished feeding is added to the feed log, so the app can show it.
- For every heart lost, one part of Suggy looks tired (a pale patch):
  eyes, then hands, then legs, then the kidney. The Check page says
  something kind and true about each one.
- At the end of a feeding Suggy's smile depends on the choices: a smile
  for no sweet picks, a flat mouth for one, a frown for two or three.

All functions here take the state dict (from state_store) and read or
change state["pet"].
"""

import datetime
import random

import state_store

# Pretend sugar level the pet starts each feeding from.
RESTING_PRETEND_SUGAR = 5.0

# How much each choice raises Suggy's pretend sugar. Made-up game numbers.
# The sweet food of a step always uses the first number, the light food
# the second one.
RISE = {
    "MEAL": (1.6, 0.9),
    "DRINK": (1.5, 0.0),
    "DESSERT": (1.4, 0.5),
}

# ---------------------------------------------------------------------------
# The food pairs. Each line is one food:
#       (id, name in lines for the card, description lines)
# A pair is (sweet food, light food). Descriptions are at most 3 lines of
# 21 letters. To add a pair, copy a pair and change it, then add a picture
# for the new ids in pet_drawing.draw_food_icon.
#
# THE WORDS ARE FOR KIDS (6 to 14): short, plain and kind. No numbers,
# no "risk", and nothing that says a food gives anyone diabetes. Some
# kids who play have diabetes themselves, and food did not cause it.
# We only say simple things about the food itself: how much sugar it
# has, and whether its energy comes fast or slowly.
# ---------------------------------------------------------------------------
FOOD_PAIRS = {
    "MEAL": [
        (("white_rice", ["White", "rice"],
          ["Turns to sugar fast."]),
         ("brown_rice", ["Brown", "rice"],
          ["Slow, steady energy."])),
        (("white_bread", ["White", "bread"],
          ["Turns to sugar fast."]),
         ("wholemeal_bread", ["Wholemeal", "bread"],
          ["More fibre.", "Keeps you full."])),
        (("sweet_cereal", ["Sweet", "cereal"],
          ["Lots of added sugar."]),
         ("oats", ["Oats"],
          ["Slow, steady energy."])),
    ],
    "DRINK": [
        (("sweet_drink", ["Sweet", "drink"],
          ["Lots of sugar,", "very fast."]),
         ("water", ["Water"],
          ["No sugar at all.", "The best drink!"])),
        (("fruit_juice", ["Fruit", "juice"],
          ["Sweet like a soft", "drink. No fibre."]),
         ("plain_tea", ["Plain", "tea"],
          ["No sugar added."])),
        (("bubble_tea", ["Bubble", "tea"],
          ["Lots and lots of", "added sugar."]),
         ("plain_milk", ["Plain", "milk"],
          ["No sugar added.", "Good for bones."])),
    ],
    "DESSERT": [
        (("ice_cream", ["Ice", "cream"],
          ["A sweet treat.", "Lots of added sugar."]),
         ("apple", ["Apple"],
          ["Sweet, with fibre.", "A good snack."])),
        (("donut", ["Donut"],
          ["A sweet treat. Lots", "of sugar and fat."]),
         ("banana", ["Banana"],
          ["Sweet, with fibre.", "Gives you energy."])),
        (("sweet_cake", ["Sweet", "cake"],
          ["A sweet treat.", "Lots of added sugar."]),
         ("plain_nuts", ["Plain", "nuts"],
          ["No sugar added.", "Keeps you full."])),
    ],
}

# The order of the steps in one feeding.
STEP_ORDER = ["MEAL", "DRINK", "DESSERT"]


def _food(step, pair_side, entry):
    """Turn one line of FOOD_PAIRS into a food dict."""
    food_id, name, about = entry
    return {
        "id": food_id,
        "name": name,
        "full_name": " ".join(name),      # e.g. "Brown rice", for lists
        "about": about,
        # pair_side 0 is the sweet food, 1 is the light one
        "kind": "sometimes" if pair_side == 0 else "everyday",
        "rise": RISE[step][pair_side],
    }


def new_feeding():
    """
    Plan one feeding: for each step pick one pair at random, and put the
    two foods on random sides (so the light food is not always on the
    same side). Returns a list of 3 steps: (title, [left food, right food]).
    """
    plan = []
    for step in STEP_ORDER:
        pair = random.choice(FOOD_PAIRS[step])
        foods = [_food(step, side, entry) for side, entry in enumerate(pair)]
        random.shuffle(foods)
        plan.append((step, foods))
    return plan


def find_food(food_id):
    """Look up a food dict by its id."""
    for step in STEP_ORDER:
        for pair in FOOD_PAIRS[step]:
            for side, entry in enumerate(pair):
                if entry[0] == food_id:
                    return _food(step, side, entry)
    return None


# ---------------------------------------------------------------------------
# Life span hearts. Suggy has up to 5 hearts.
# A feeding that pushes the pretend sugar to HIGH_SUGAR or more takes 1
# heart away (this happens with two or three sweet choices). A feeding
# below that gives 1 heart back. At 0 hearts Suggy falls asleep. Waking
# up gives all the hearts back. Cosmetics and points stay.
# ---------------------------------------------------------------------------
MAX_HEARTS = 5
HIGH_SUGAR = 8.0


def feed(state, food_ids, now=None):
    """
    Feed Suggy one whole feeding: food_ids is the list of the three foods
    picked (meal, drink, dessert). Changes the state in place and returns
    the "last_meal" record (with the pretend sugar level).
    """
    now = now or datetime.datetime.now()
    pet = state["pet"]
    foods = [find_food(food_id) for food_id in food_ids]

    for food in foods:
        if food["kind"] == "everyday":
            pet["everyday_foods_eaten"] += 1
        else:
            pet["sometimes_foods_eaten"] += 1

    # 10 points for each light choice.
    light_picks = sum(1 for food in foods if food["kind"] == "everyday")
    points = light_picks * state_store.POINTS_PER_REWARD
    state_store.add_points(state, points)

    total_rise = sum(food["rise"] for food in foods)
    record = {
        "foods": list(food_ids),
        "food_names": [food["full_name"] for food in foods],
        "points": points,
        # how many of the three picks were the sweet food (0 to 3)
        "sweet_picks": sum(1 for food in foods if food["kind"] == "sometimes"),
        "pretend_sugar": round(RESTING_PRETEND_SUGAR + total_rise, 1),
        "at": now.replace(microsecond=0).isoformat(),
    }
    # More sugar = fewer hearts; lighter feedings refill them.
    if record["pretend_sugar"] >= HIGH_SUGAR:
        pet["hearts"] = max(0, pet["hearts"] - 1)
        record["hearts_change"] = -1
        if pet["hearts"] == 0:
            pet["awake"] = False        # the pet screen shows Suggy asleep
            record["fell_asleep"] = True
    else:
        pet["hearts"] = min(MAX_HEARTS, pet["hearts"] + 1)
        record["hearts_change"] = 1

    pet["last_meal"] = record
    pet["mood"] = "happy"
    # Keep it in the feed log for the app (only the newest ones).
    state["feed_log"].append(record)
    del state["feed_log"][:-state_store.KEEP_FEEDINGS]
    return record


def mood_after(record):
    """Suggy's face at the end of a feeding: the smile fades with sugar."""
    sweet = record.get("sweet_picks", 0)
    if sweet == 0:
        return "happy"
    if sweet == 1:
        return "okay"
    return "sad"


# ---------------------------------------------------------------------------
# Check on Suggy. For each heart Suggy has lost, one more part looks
# tired (a pale patch), in this order: eyes, hands, legs, kidney. These
# are the parts doctors look after in people with diabetes.
# The words are kind and simple, made for kids: they say what steady
# sugar HELPS, not what can go wrong. They are general facts, not a
# diagnosis and not advice. Each one is at most 3 lines of 21 letters.
# ---------------------------------------------------------------------------
BODY_PARTS = [
    ("eyes", "Eyes",
     ["Steady sugar helps", "eyes see clearly."]),
    ("hands", "Hands",
     ["Steady sugar helps", "hands feel things", "well."]),
    ("legs", "Legs",
     ["Steady sugar helps", "legs and feet stay", "strong."]),
    ("kidney", "Kidney",
     ["Steady sugar helps", "kidneys clean the", "blood."]),
]


def sore_parts(state):
    """
    The body parts that look tired right now: one for each heart lost
    (5 hearts = none, 4 = eyes, 3 = eyes and hands, and so on).
    """
    lost = MAX_HEARTS - state["pet"]["hearts"]
    return [part for part, _name, _fact in BODY_PARTS[:max(0, lost)]]


def wake_up(state):
    """
    Suggy wakes up after a sleep: all the hearts are back. Nothing is
    lost: the cosmetics and the points stay.
    """
    pet = state["pet"]
    pet["awake"] = True
    pet["hearts"] = MAX_HEARTS
    pet["last_meal"] = None
    pet["mood"] = "happy"
