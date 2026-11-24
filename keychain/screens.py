"""
screens.py - shared screen helpers, the Hello page and the menu.

The keychain has three buttons. They do the SAME job on every page:
    left arrow, right arrow   move between the choices
    OK                        pick the choice / carry on

Each screen is a class with these methods:
    draw()      draw itself on the screen canvas
    left()      the left arrow button
    right()     the right arrow button
    ok()        the OK button
    refresh()   (optional) re-read state.json and redraw if needed;
                main.py calls it every second
    stop()      (optional) stop any timers when another screen shows

Few words on every page, and no text smaller than TINY.

The feature screens live in their own files:
    pet_screen.py      Feed Suggy
    insulin_screen.py  Insulin reminder
    kid_quiz.py        Quiz for kids
    check_screen.py    Check on Suggy
"""

import math

import feeding
import pet_drawing
import state_store
from keychain_frame import (SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_BG, SCREEN_INK,
                            SCREEN_RIM, SCREEN_RIM_INNER, rounded_points)

# A blocky monospace font gives a "pixel screen" feel without images.
# Sizes are large on purpose. TINY is only for the food descriptions.
TINY = ("Courier", 11, "bold")
SMALL = ("Courier", 12, "bold")
NORMAL = ("Courier", 14, "bold")
BIG = ("Courier", 26, "bold")
MID = SCREEN_WIDTH // 2


# The glass of the screen is a rounded shape, a little bigger than the
# 200 x 160 drawing area, so nothing sits right against its edge.
GLASS_GROW = 4        # pixels the glass sticks out past the drawing area
GLASS_RADIUS = 26     # how round its corners are


def _glass_inset(distance_from_edge):
    """
    How far the rounded corner cuts in, at this distance from the top or
    bottom edge of the glass. 0 once we are past the rounded part.
    """
    if distance_from_edge >= GLASS_RADIUS:
        return 0
    gap = GLASS_RADIUS - distance_from_edge
    return GLASS_RADIUS - math.sqrt(GLASS_RADIUS ** 2 - gap ** 2)


def draw_pixel_background(canvas):
    """
    Clear the screen and draw the rounded glass with faint grid lines
    every 4 pixels (the grid makes it look like a tiny low-resolution LCD).
    The soft rims make the screen blend into the keychain instead of
    looking like a sharp rectangle.
    """
    canvas.delete("all")
    g = GLASS_GROW
    left, top, right, bottom = -g, -g, SCREEN_WIDTH + g, SCREEN_HEIGHT + g

    # Soft outer rim, thin darker edge, then the glass itself.
    for grow, colour in ((2, SCREEN_RIM), (0, SCREEN_RIM_INNER),
                         (-1.5, SCREEN_BG)):
        outline = rounded_points(left - grow, top - grow, right + grow,
                                 bottom + grow, GLASS_RADIUS + grow)
        canvas.create_polygon([v for point in outline for v in point],
                              fill=colour, outline="")

    # Grid lines, cut short near the rounded corners.
    grid = "#bcd898"
    for x in range(0, SCREEN_WIDTH + 1, 4):
        cut = _glass_inset(min(x - left, right - x)) + 2
        canvas.create_line(x, top + cut, x, bottom - cut, fill=grid)
    for y in range(0, SCREEN_HEIGHT + 1, 4):
        cut = _glass_inset(min(y - top, bottom - y)) + 2
        canvas.create_line(left + cut, y, right - cut, y, fill=grid)


def text(canvas, y, words, font=SMALL, x=MID):
    """Write one centred line of text in the screen's ink colour."""
    canvas.create_text(x, y, text=words, font=font, fill=SCREEN_INK)


def draw_hints(canvas, ok):
    """
    The dark box along the bottom that says what OK does on this page,
    for example  [OK: start].
    """
    canvas.create_rectangle(40, 133, 160, 154, fill=SCREEN_INK,
                            outline=SCREEN_INK)
    canvas.create_text(MID, 144, text="OK: " + ok, font=SMALL,
                       fill=SCREEN_BG)


def draw_card(canvas, x1, y1, x2, y2, chosen):
    """
    One of two side-by-side choice cards. The chosen one has a thick
    border; the arrows move it. Returns nothing, the caller draws inside.
    """
    canvas.create_rectangle(x1, y1, x2, y2, fill=SCREEN_BG,
                            outline=SCREEN_INK, width=4 if chosen else 1)


def draw_list(canvas, items, index, top, row_height=28, visible=4,
              font=NORMAL):
    """
    Draw a list of choices with the chosen one highlighted (dark row,
    light text). If there are more items than fit, the list
    scrolls so the chosen one is always visible, and small ^ / v marks
    show there is more above or below.
    """
    # Which item is at the top of the visible window?
    first = 0 if index < visible else index - visible + 1

    for row in range(visible):
        i = first + row
        if i >= len(items):
            break
        y = top + row * row_height
        selected = (i == index)
        if selected:
            canvas.create_rectangle(8, y - row_height // 2 + 1,
                                    SCREEN_WIDTH - 8, y + row_height // 2 - 1,
                                    fill=SCREEN_INK, outline=SCREEN_INK)
        canvas.create_text(MID, y, text=items[i], font=font,
                           fill=SCREEN_BG if selected else SCREEN_INK)

    if first > 0:
        canvas.create_text(SCREEN_WIDTH - 4, top - 4, text="^",
                           font=SMALL, fill=SCREEN_INK)
    if first + visible < len(items):
        canvas.create_text(SCREEN_WIDTH - 4,
                           top + (visible - 1) * row_height + 4, text="v",
                           font=SMALL, fill=SCREEN_INK)


class WelcomeScreen:
    """
    The first page when the keychain turns on.
        Linked in the app:  "Hello <nickname>!"
        Not linked:         "Hello! I'm Suggy"
    OK = start (go to the menu). The small Home button always comes
    back to this page.
    """

    def __init__(self, canvas, on_start):
        self.canvas = canvas
        self.on_start = on_start
        self.last_seen = None

    def _what_to_show(self, state):
        """The things that change this page (so we know when to redraw)."""
        link = state["link"]
        return (link["linked"], link["nickname"],
                tuple(state["pet"]["accessories"]), state["pet"]["awake"],
                state["pet"]["hearts"])

    def draw(self):
        c = self.canvas
        draw_pixel_background(c)
        state = state_store.load_state()
        self.last_seen = self._what_to_show(state)
        link = state["link"]

        if link["linked"]:
            text(c, 18, "Hello " + (link["nickname"] or "friend") + "!",
                 NORMAL)
        else:
            text(c, 18, "Hello! I'm Suggy", NORMAL)
        if state["pet"]["awake"]:
            pet_drawing.draw_pet(c, MID, 80, "happy",
                                 accessories=state["pet"]["accessories"],
                                 sore=feeding.sore_parts(state))
        else:
            # Suggy is asleep (0 hearts). Feed -> OK wakes Suggy up.
            pet_drawing.draw_pet(c, MID, 80, "sleepy",
                                 accessories=state["pet"]["accessories"])
        draw_hints(c, "start")

    def refresh(self):
        """Redraw only if something on this page changed."""
        if self._what_to_show(state_store.load_state()) != self.last_seen:
            self.draw()

    def ok(self):
        self.on_start()

    def left(self):
        pass

    def right(self):
        pass


class MainMenuScreen:
    """
    The menu: four cards, two on top and two below:
        Feed     Insulin
        Check    Quiz
    Arrows = move the thick border, OK = open that one.

    on_select is a function from main.py, called with "nutrition",
    "insulin", "check" or "quiz", plus the menu position (so coming
    back from a feature lands on the same choice).
    """

    ITEMS = [("Feed", "nutrition"), ("Insulin", "insulin"),
             ("Check", "check"), ("Quiz", "quiz")]

    def __init__(self, canvas, on_select, on_back=None, start_index=0):
        self.canvas = canvas
        self.on_select = on_select
        self.index = min(start_index, len(self.ITEMS) - 1)

    def draw(self):
        c = self.canvas
        draw_pixel_background(c)
        for i, (label, name) in enumerate(self.ITEMS):
            # Two cards in each row: i = 0, 1 on top and 2, 3 below.
            x1 = 6 + (i % 2) * 96
            y1 = 4 + (i // 2) * 63
            draw_card(c, x1, y1, x1 + 92, y1 + 60, chosen=(i == self.index))
            x, y = x1 + 46, y1 + 22
            if name == "nutrition":
                pet_drawing.draw_food_icon(c, x, y, "white_rice")
            elif name == "insulin":
                pet_drawing.draw_bell(c, x, y)
            elif name == "check":
                pet_drawing.draw_heart_icon(c, x, y - 1)
            else:
                # The quiz picture is simply a big question mark.
                c.create_text(x, y, text="?", font=BIG, fill=SCREEN_INK)
            c.create_text(x, y1 + 49, text=label, font=SMALL,
                          fill=SCREEN_INK)
        draw_hints(c, "open")

    def ok(self):
        _label, name = self.ITEMS[self.index]
        self.on_select(name, self.index)

    def left(self):
        self.index = (self.index - 1) % len(self.ITEMS)
        self.draw()

    def right(self):
        self.index = (self.index + 1) % len(self.ITEMS)
        self.draw()
