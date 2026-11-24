"""
pet_screen.py - the Feed Suggy feature.

Suggy can be fed at any time. A feeding goes step by step: MEAL, then
DRINK, then DESSERT. Each step shows two very different foods side by
side, with a short description of the chosen one underneath, so the
player can compare them. The foods change from feeding to feeding.

What the screen shows (self.mode):
  "choose"   - arrows move between the two foods, OK feeds that one and
               goes to the next step
  "eating"   - short eating animation after each pick
  "result"   - after the 3 steps: Suggy's pretend sugar level and hearts.
               Suggy smiles for no sweet picks, has a flat mouth for one
               and a frown for two or three.
  "sleeping" - Suggy ran out of hearts and fell asleep (OK = wake up)
  "woke"     - Suggy is awake again with full hearts (OK = start feeding)

The small Home button leaves at any time; a feeding that is not finished
is simply not saved.

The rules (foods, figures, hearts) live in feeding.py.
The drawings live in pet_drawing.py.
"""

import feeding
import pet_drawing
import state_store
from keychain_frame import SCREEN_WIDTH, SCREEN_INK, SCREEN_BG
from screens import (draw_pixel_background, draw_hints, draw_card, text,
                     MID, TINY, SMALL)


class PetFeedingScreen:

    def __init__(self, canvas, on_back):
        self.canvas = canvas
        self.on_back = on_back
        self.active = True        # set to False when another screen shows
        self.plan = feeding.new_feeding()   # the 3 steps of this feeding
        self.step = 0             # 0 = meal, 1 = drink, 2 = dessert
        self.side = 0             # 0 = left food, 1 = right food
        self.picked = []          # food ids picked so far in this feeding
        self.result = None        # last_meal record while showing a result
        self.state = state_store.load_state()
        self.mode = "choose" if self.state["pet"]["awake"] else "sleeping"

    def stop(self):
        """Called by main.py when this screen is replaced."""
        self.active = False

    def foods(self):
        """The two foods of the step we are on."""
        return self.plan[self.step][1]

    # ---- Drawing -----------------------------------------------------------

    def draw(self, mouth_open=False, bite_size=0):
        c = self.canvas
        draw_pixel_background(c)
        pet = self.state["pet"]

        if self.mode in ("sleeping", "woke"):
            self._draw_sleep()
            return
        if self.mode == "choose":
            self._draw_choice()
            return

        if self.mode == "eating":
            title, mood = "NOM NOM", "happy"
        else:
            # The result: Suggy's smile fades with the sweet choices.
            mood = feeding.mood_after(self.result)
            title = {"happy": "YUM!", "okay": "HMM...", "sad": "OOF..."}[mood]

        # Title top-left, life span hearts top-right.
        c.create_text(10, 11, text=title, anchor="w", font=SMALL,
                      fill=SCREEN_INK)
        pet_drawing.draw_hearts(c, SCREEN_WIDTH - 66, 5, pet["hearts"],
                                feeding.MAX_HEARTS)
        pet_drawing.draw_pet(c, MID, 56, mood, mouth_open=mouth_open,
                             accessories=pet["accessories"],
                             sore=feeding.sore_parts(self.state))

        if self.mode == "eating":
            pet_drawing.draw_food_bite(c, MID, 90, bite_size)
        elif self.mode == "result":
            text(c, 98, "Pretend sugar %.1f" % self.result["pretend_sugar"])
            hearts = "+1 heart" if self.result["hearts_change"] > 0 else "-1 heart"
            text(c, 116, "%s  +%d pts" % (hearts, self.result["points"]))
            draw_hints(c, "done")

    def _draw_choice(self):
        """Two food cards side by side, and the chosen food's description."""
        c = self.canvas
        title = self.plan[self.step][0]
        c.create_text(10, 10, anchor="w", font=SMALL, fill=SCREEN_INK,
                      text="%d/3 %s" % (self.step + 1, title))
        pet_drawing.draw_hearts(c, SCREEN_WIDTH - 66, 4,
                                self.state["pet"]["hearts"],
                                feeding.MAX_HEARTS)
        for i, food in enumerate(self.foods()):
            x1 = 6 + i * 96
            chosen = (i == self.side)
            draw_card(c, x1, 20, x1 + 92, 102, chosen)
            pet_drawing.draw_food_icon(c, x1 + 46, 43, food["id"])
            # The name, on a dark band if this card is the chosen one.
            if chosen:
                c.create_rectangle(x1, 66, x1 + 92, 102, fill=SCREEN_INK,
                                   outline=SCREEN_INK)
            lines = food["name"]
            # A long word (like "Wholemeal") uses the slightly smaller font.
            font = TINY if max(len(line) for line in lines) > 8 else SMALL
            y = 84 - (len(lines) - 1) * 8
            for line in lines:
                c.create_text(x1 + 46, y, text=line, font=font,
                              fill=SCREEN_BG if chosen else SCREEN_INK)
                y += 16
        # The description of the chosen food (see the sources in feeding.py).
        about = self.foods()[self.side]["about"]
        y = 129 - (len(about) - 1) * 8
        for line in about:
            text(c, y, line, TINY)
            y += 16

    def _draw_sleep(self):
        """Suggy asleep after too much sugar, and Suggy awake again."""
        c = self.canvas
        pet = self.state["pet"]
        if self.mode == "sleeping":
            pet_drawing.draw_pet(c, MID, 52, "sleepy",
                                 accessories=pet["accessories"])
            text(c, 96, "Suggy is tired")
            text(c, 114, "and fell asleep.")
            draw_hints(c, "wake up")
        else:  # woke
            pet_drawing.draw_pet(c, MID, 56, "happy",
                                 accessories=pet["accessories"])
            pet_drawing.draw_hearts(c, SCREEN_WIDTH - 66, 5, feeding.MAX_HEARTS)
            text(c, 106, "Good morning!")
            draw_hints(c, "feed")

    # ---- Animations --------------------------------------------------------

    def _animate_eating(self, frame=0):
        """
        6 frames, 150 ms apart: Suggy opens and closes its mouth while the
        food piece gets smaller. Then the next step (or the result) shows.
        """
        if not self.active:
            return
        if frame < 6:
            self.draw(mouth_open=(frame % 2 == 0), bite_size=7 - frame)
            self.canvas.after(150, lambda: self._animate_eating(frame + 1))
        elif self.result:
            self.mode = "result"       # all three steps are done
            self.draw()
        else:
            self.mode = "choose"       # on to the drink or the dessert
            self.draw()

    # ---- Buttons -----------------------------------------------------------

    def left(self):
        if self.mode == "choose":
            self.side = 0
            self.draw()

    def right(self):
        if self.mode == "choose":
            self.side = 1
            self.draw()

    def ok(self):
        if self.mode == "choose":
            self._pick()
        elif self.mode == "result":
            if self.result.get("fell_asleep"):
                self.result = None
                self.mode = "sleeping"
                self.draw()
            else:
                self.on_back()           # feeding done: back to the menu
        elif self.mode == "sleeping":
            # Suggy wakes up with all the hearts back. Nothing is lost.
            self.state = state_store.update_state(feeding.wake_up)
            self.mode = "woke"
            self.draw()
        elif self.mode == "woke":
            self.mode = "choose"
            self.draw()

    def _pick(self):
        """OK on a food: Suggy eats it, then the next step comes."""
        self.picked.append(self.foods()[self.side]["id"])
        if self.step < len(self.plan) - 1:
            self.step += 1
            self.side = 0
        else:
            # Last step: save the whole feeding straight away, so it
            # counts even if the window is closed during the animation.
            picked = list(self.picked)
            self.state = state_store.update_state(
                lambda state: feeding.feed(state, picked))
            self.result = self.state["pet"]["last_meal"]
        self.mode = "eating"
        self._animate_eating()
