"""
check_screen.py - the Check on Suggy feature.

On this page the player sees how Suggy is doing: for every heart Suggy
has lost, one more body part looks tired (a soft pale patch). These are
the parts doctors look after in people with diabetes.

    5 hearts  no marks          2 hearts  eyes, hands, legs
    4 hearts  eyes              1 heart   eyes, hands, legs, kidney
    3 hearts  eyes, hands

The arrows move through the four parts, and a short fact about the
chosen part is shown at the bottom. The facts are kind and simple: they
say what steady sugar helps. OK goes back to the menu.

The facts and the order of the parts live in feeding.py (BODY_PARTS).
They are general health facts, not a diagnosis and not advice.
"""

import feeding
import pet_drawing
import state_store
from keychain_frame import SCREEN_WIDTH, SCREEN_INK, SCREEN_BG
from screens import draw_pixel_background, text, TINY, SMALL


class CheckScreen:
    def __init__(self, canvas, on_back):
        self.canvas = canvas
        self.on_back = on_back
        self.index = 0            # which body part is chosen
        self.last_seen = None

    def _what_to_show(self, state):
        """The things that change this page (so we know when to redraw)."""
        pet = state["pet"]
        return (pet["hearts"], pet["awake"], tuple(pet["accessories"]))

    def draw(self):
        c = self.canvas
        draw_pixel_background(c)
        state = state_store.load_state()
        self.last_seen = self._what_to_show(state)
        pet = state["pet"]
        sore = feeding.sore_parts(state)

        # Title top-left, life span hearts top-right.
        c.create_text(10, 11, text="CHECK", anchor="w", font=SMALL,
                      fill=SCREEN_INK)
        pet_drawing.draw_hearts(c, SCREEN_WIDTH - 66, 5, pet["hearts"],
                                feeding.MAX_HEARTS)

        # Suggy on the left, with the sore marks.
        if pet["awake"]:
            mood = "happy" if not sore else ("okay" if len(sore) < 3 else "sad")
            pet_drawing.draw_pet(c, 52, 64, mood,
                                 accessories=pet["accessories"], sore=sore)
        else:
            pet_drawing.draw_pet(c, 52, 64, "sleepy",
                                 accessories=pet["accessories"])

        # The four body parts on the right. A soft striped box means "tired".
        for row, (part, name, _fact) in enumerate(feeding.BODY_PARTS):
            y = 34 + row * 20
            chosen = (row == self.index)
            if chosen:
                c.create_rectangle(102, y - 9, 195, y + 9, fill=SCREEN_INK,
                                   outline=SCREEN_INK)
            c.create_text(108, y, anchor="w", text=name, font=SMALL,
                          fill=SCREEN_BG if chosen else SCREEN_INK)
            if part in sore:
                pet_drawing.draw_sore_box(c, 176, y - 7, 190, y + 7)

        # A short fact about the chosen part.
        fact = feeding.BODY_PARTS[self.index][2]
        y = 114
        for line in fact:
            text(c, y, line, TINY)
            y += 15

    def refresh(self):
        """Redraw if Suggy's hearts changed."""
        if self._what_to_show(state_store.load_state()) != self.last_seen:
            self.draw()

    def left(self):
        self.index = (self.index - 1) % len(feeding.BODY_PARTS)
        self.draw()

    def right(self):
        self.index = (self.index + 1) % len(feeding.BODY_PARTS)
        self.draw()

    def ok(self):
        self.on_back()   # OK goes back to the menu
