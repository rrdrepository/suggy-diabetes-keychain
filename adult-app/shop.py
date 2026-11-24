"""
shop.py - the cosmetics in the shop, and buying and wearing them.

>>> PLACEHOLDER ITEMS AND PRICES. The team has not decided them yet. <<<
To change the shop, edit SHOP below. This is the only place.

The shop has 3 categories with 5 items each. Suggy wears at most ONE
item from each category at a time (one on the head, one on the eyes,
one round the neck).

Each item is (id, name, price):
    id     - the name the drawing code uses. The drawings are in
             pet_drawing.py (draw_accessories). A new id also needs a
             new drawing there, in BOTH copies of pet_drawing.py
             (keychain/ and adult-app/).
    name   - what the shop shows
    price  - how many points it costs
"""

import state_store

SHOP = [
    ("Head", [
        ("cap",            "Cap",            20),
        ("beanie",         "Beanie",         20),
        ("bow",            "Hair bow",       30),
        ("top_hat",        "Top hat",        40),
        ("crown",          "Crown",          60),
    ]),
    ("Eyes", [
        ("glasses",        "Round glasses",  20),
        ("square_glasses", "Square glasses", 20),
        ("sunglasses",     "Sunglasses",     30),
        ("monocle",        "Monocle",        40),
        ("goggles",        "Goggles",        50),
    ]),
    ("Neck", [
        ("scarf",          "Scarf",          20),
        ("bow_tie",        "Bow tie",        20),
        ("necktie",        "Necktie",        30),
        ("necklace",       "Necklace",       40),
        ("medal",          "Medal",          60),
    ]),
]


def find_item(item_id):
    """Returns (category name, name, price) for an id, or None."""
    for category, items in SHOP:
        for an_id, name, price in items:
            if an_id == item_id:
                return category, name, price
    return None


def ids_in_category(category):
    for name, items in SHOP:
        if name == category:
            return [an_id for an_id, _name, _price in items]
    return []


def owned_items(state):
    """Everything bought so far (anything worn counts as owned too)."""
    pet = state["pet"]
    return list(dict.fromkeys(pet["owned"] + pet["accessories"]))


def _put_on(pet, item_id, category):
    """Wear this item instead of anything else from the same category."""
    same = ids_in_category(category)
    pet["accessories"] = [a for a in pet["accessories"] if a not in same]
    pet["accessories"].append(item_id)


def buy(item_id):
    """
    Try to buy one item. Suggy puts it on straight away.
    Returns (True, message) or (False, message).

    The check and the change happen together inside update_state, so the
    points can never go below zero, even if the keychain saves at the
    same moment.
    """
    found = find_item(item_id)
    if found is None:
        return False, "That item is not in the shop."
    category, name, price = found
    result = {}

    def change(state):
        pet = state["pet"]
        if item_id in owned_items(state):
            result["message"] = "You already own the %s." % name
        elif state["points"]["balance"] < price:
            short = price - state["points"]["balance"]
            result["message"] = "You need %d more points." % short
        else:
            state["points"]["balance"] -= price
            pet["owned"] = owned_items(state) + [item_id]
            _put_on(pet, item_id, category)
            result["ok"] = True
            result["message"] = ("Bought the %s! Suggy is wearing it here "
                                 "and on the keychain." % name)
    state_store.update_state(change)
    return result.get("ok", False), result["message"]


def wear(item_id):
    """Put on an item that is already owned."""
    found = find_item(item_id)

    def change(state):
        if found and item_id in owned_items(state):
            _put_on(state["pet"], item_id, found[0])
    state_store.update_state(change)


def take_off(item_id):
    """Take an item off (it stays owned)."""
    def change(state):
        pet = state["pet"]
        pet["owned"] = owned_items(state)        # keep it owned
        pet["accessories"] = [a for a in pet["accessories"] if a != item_id]
    state_store.update_state(change)
