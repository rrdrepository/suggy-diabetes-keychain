"""
vouchers.py - exchange points for vouchers (DEMO ONLY).

>>> PLACEHOLDER VOUCHERS AND COSTS. Vendors are not confirmed yet. <<<
To change them, edit VOUCHERS below. This is the only place.

Nothing here is real: no vendor is contacted, nothing is booked and the
codes cannot be used anywhere. The app says so on the Vouchers tab.

The MAIN reward is seeing a doctor. Those vouchers are shown first, in
a highlighted box. The other vouchers are price-off vouchers in three
groups:
    Pharmacy     for example money off insulin and test strips
    Equipment    things people use every day, with items made for kids
    Food swaps   the lighter food made cheaper than the sweet one
                 (brown rice instead of white rice), matching the food
                 pairs on the keychain

The users are children aged 6 to 14, so a parent or guardian is
the one who would use a voucher. Insulin is a prescription medicine, so
that voucher says "with a doctor's prescription".

Each voucher is (id, kind, title, short note, cost in points).
The note may be "".
"""

import random

import state_store

MAIN_KIND = "Doctor consultation"     # shown first, highlighted

VOUCHERS = [
    ("consult",    "Doctor consultation", "Diabetes consultation with a doctor",
     "", 300),
    ("screen",     "Doctor consultation", "Blood sugar screening",
     "", 200),

    ("insulin",    "Pharmacy", "RM10 off insulin",
     "with a doctor's prescription", 150),
    ("strips",     "Pharmacy", "RM5 off glucose test strips",
     "", 80),
    ("lancets",    "Pharmacy", "RM5 off lancets",
     "finger-prick needles", 60),
    ("pen_needles", "Pharmacy", "RM5 off insulin pen needles",
     "", 60),

    ("meter",      "Equipment", "RM20 off a blood glucose meter",
     "small, simple model for kids", 200),
    ("bracelet",   "Equipment", "RM10 off a medical ID bracelet",
     "kids' sizes", 100),
    ("cool_pouch", "Equipment", "RM10 off an insulin cooling pouch",
     "fits a school bag", 100),
    ("bottle",     "Equipment", "RM10 off a water bottle",
     "", 80),
    ("shoes",      "Equipment", "RM10 off sports shoes",
     "", 150),

    ("brown_rice", "Food swaps", "RM5 off brown rice",
     "instead of white rice", 100),
    ("wholemeal",  "Food swaps", "RM3 off wholemeal bread",
     "instead of white bread", 60),
    ("oats",       "Food swaps", "RM3 off oats",
     "instead of sweet cereal", 60),
    ("milk",       "Food swaps", "RM2 off plain milk",
     "instead of bubble tea", 40),
    ("fruit",      "Food swaps", "RM3 off fresh fruit",
     "instead of ice cream or cake", 60),
]


def kinds():
    """The groups other than the main one, in the order of the list."""
    result = []
    for _id, kind, _title, _note, _cost in VOUCHERS:
        if kind != MAIN_KIND and kind not in result:
            result.append(kind)
    return result


# Letters and digits that are easy to read (no 0/O or 1/I).
CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def make_code():
    """A made-up voucher code such as 'DEMO-7KQ2-XM4P'."""
    def part():
        return "".join(random.choice(CODE_LETTERS) for _ in range(4))
    return "DEMO-%s-%s" % (part(), part())


def claim(voucher_id):
    """
    Exchange points for one voucher. Returns (True, message, code) or
    (False, message, None). The check and the change happen together
    inside update_state, so the points can never go below zero.
    """
    found = next((v for v in VOUCHERS if v[0] == voucher_id), None)
    if found is None:
        return False, "That voucher is not on the list.", None
    _id, kind, title, note, cost = found
    result = {}

    def change(state):
        if state["points"]["balance"] < cost:
            short = cost - state["points"]["balance"]
            result["message"] = "You need %d more points." % short
            return
        state["points"]["balance"] -= cost
        code = make_code()
        state["vouchers"].append({
            "id": voucher_id,
            "kind": kind,
            "title": title,
            "note": note,
            "cost": cost,
            "code": code,
            "claimed_at": state_store.now_text(),
        })
        result["code"] = code
        result["message"] = "Claimed! Your demo code is %s" % code
    state_store.update_state(change)
    return "code" in result, result["message"], result.get("code")
