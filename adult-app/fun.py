"""
fun.py - the friendly look and the little animations of the companion app.

Everything "motion" lives here, so the page files stay simple:

    apply_theme(root)     warm colours, bigger tabs, buttons that light up
                          when the mouse is over them
    CountUp(label, ...)   a number that counts up (or down) to its new
                          value instead of jumping
    Bouncer               makes a picture of Suggy bob gently up and down,
                          and jump when it is clicked
    Header(root)          the banner at the top: Suggy waving, the title
                          and the points
    celebrate(root, ...)  a short pop-up card with falling confetti and a
                          jumping Suggy, for happy moments

Only Tkinter is used. Animations work with root.after(): a function
draws one frame, then asks Tkinter to call it again a moment later.
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk

import pet_drawing

# ---- Colours ---------------------------------------------------------------
CREAM = "#fff7ea"        # the window background
CARD = "#ffffff"         # boxes you can type in, tables
INK = "#40312b"          # normal text
ORANGE = "#f5a623"       # buttons (the same orange as the keychain buttons)
ORANGE_LIGHT = "#ffc24d"  # a button with the mouse over it
ORANGE_DARK = "#d98c0f"  # a button being pressed
PINK = "#e9636c"         # the keychain's body colour, used for the banner
GREEN = "#2e7d32"
TAB_IDLE = "#f3dcc0"     # tabs that are not open
DISABLED = "#eadfd0"     # buttons that cannot be pressed now

CARD_HOVER = "#ffeccc"    # a white answer button with the mouse over it
# Which colour a button turns when the mouse is over it, and back again.
HOVER = {ORANGE: ORANGE_LIGHT, CARD: CARD_HOVER}
UNHOVER = {ORANGE_LIGHT: ORANGE, CARD_HOVER: CARD}

CONFETTI_COLOURS = ["#e9636c", "#f5a623", "#2f66c9", "#2e7d32", "#f2b632",
                    "#9b59b6"]

FRAME_MS = 33            # one animation frame (about 30 frames a second)


# ---------------------------------------------------------------------------
# The look
# ---------------------------------------------------------------------------

def apply_theme(root):
    """
    Set the colours and fonts for the whole app. Call this once, BEFORE
    the pages are built, so every widget picks the new look up.
    """
    root.configure(bg=CREAM)
    # option_add sets a default for every widget made after this line.
    root.option_add("*Background", CREAM)
    root.option_add("*Foreground", INK)
    root.option_add("*Entry.Background", CARD)
    root.option_add("*Spinbox.Background", CARD)
    # Buttons: flat, orange and roomy, with a hand cursor.
    root.option_add("*Button.Background", ORANGE)
    root.option_add("*Button.Foreground", "#3d2a00")
    root.option_add("*Button.activeBackground", ORANGE_DARK)
    root.option_add("*Button.disabledForeground", "#a89c8c")
    root.option_add("*Button.relief", "flat")
    root.option_add("*Button.borderWidth", 0)
    root.option_add("*Button.cursor", "hand2")
    root.option_add("*Button.padX", 10)
    # The choice buttons (Head / Eyes / Neck, Pharmacy / Equipment ...).
    root.option_add("*Radiobutton.Background", TAB_IDLE)
    root.option_add("*Radiobutton.selectColor", ORANGE)
    root.option_add("*Radiobutton.activeBackground", ORANGE_LIGHT)
    root.option_add("*Radiobutton.relief", "flat")
    root.option_add("*Radiobutton.borderWidth", 0)
    root.option_add("*Radiobutton.cursor", "hand2")
    root.option_add("*Checkbutton.cursor", "hand2")

    # The tabs and tables are "ttk" widgets. They have their own styles.
    style = ttk.Style(root)
    style.theme_use("clam")       # a theme that lets us choose the colours
    style.configure("TNotebook", background=CREAM, borderwidth=0)
    style.configure("TNotebook.Tab", background=TAB_IDLE, foreground=INK,
                    padding=(10, 6), font=("Arial", 10, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", ORANGE), ("active", ORANGE_LIGHT),
                          ("disabled", CREAM)],
              foreground=[("disabled", "#c9bba8")],
              # The open tab is a little bigger than the others.
              padding=[("selected", (14, 8))])
    style.configure("Treeview", background=CARD, fieldbackground=CARD,
                    foreground=INK, rowheight=22)
    style.configure("Treeview.Heading", background=TAB_IDLE, foreground=INK,
                    font=("Arial", 9, "bold"))

    _add_button_hover(root)


def _add_button_hover(root):
    """
    Make every orange button light up while the mouse is over it.
    bind_class() adds the behaviour to ALL buttons at once, so the page
    files do not have to do anything.
    """
    def enter(event):
        button = event.widget
        if str(button["state"]) != "disabled" and button["bg"] in HOVER:
            button.configure(bg=HOVER[button["bg"]])

    def leave(event):
        button = event.widget
        if button["bg"] in UNHOVER:
            button.configure(bg=UNHOVER[button["bg"]])

    root.bind_class("Button", "<Enter>", enter, add="+")
    root.bind_class("Button", "<Leave>", leave, add="+")


def set_enabled(button, enabled):
    """
    Switch a button on or off, and colour it to match: orange when it
    can be pressed, pale when it cannot.
    """
    if enabled:
        if str(button["state"]) == "disabled":
            button.configure(state="normal", bg=ORANGE, cursor="hand2")
    else:
        button.configure(state="disabled", bg=DISABLED, cursor="")


# ---------------------------------------------------------------------------
# A number that counts up
# ---------------------------------------------------------------------------

class CountUp:
    """
    Shows a number in a label, e.g. "120 points". When the number
    changes, the label counts from the old value to the new one in
    about half a second instead of jumping.

        points = CountUp(label, "%d points")
        points.set(120)
    """

    SECONDS = 0.6

    def __init__(self, label, text="%d"):
        self.label = label
        self.text = text
        self.shown = None        # the number on the label right now
        self.target = None
        self.start = 0
        self.started_at = 0

    def set(self, value):
        if self.shown is None:   # the very first value: just show it
            self.shown = self.target = value
            self.label.config(text=self.text % value)
            return
        if value == self.target:
            return
        running = self.shown != self.target
        self.start, self.target = self.shown, value
        self.started_at = time.perf_counter()
        if not running:
            self._step()

    def _step(self):
        if not self.label.winfo_exists():
            return
        t = min(1.0, (time.perf_counter() - self.started_at) / self.SECONDS)
        ease = 1 - (1 - t) ** 3              # fast at first, then gentle
        self.shown = round(self.start + (self.target - self.start) * ease)
        if t >= 1.0:
            self.shown = self.target
        self.label.config(text=self.text % self.shown)
        if self.shown != self.target:
            self.label.after(FRAME_MS, self._step)


# ---------------------------------------------------------------------------
# Suggy bobbing and jumping
# ---------------------------------------------------------------------------

class Bouncer:
    """
    Keeps a picture alive: it calls draw(offset) about 30 times a
    second, where offset is how many pixels to move Suggy up (minus) or
    down (plus). Suggy bobs gently, and jump() makes one happy jump.

    draw is a function from the page that owns the picture. Nothing is
    drawn while the picture is hidden (another tab is open).
    """

    def __init__(self, canvas, draw):
        self.canvas = canvas
        self.draw = draw
        self.jump_started = None
        self.last_offset = None
        self.redraw = True              # set to True to force a new drawing
        canvas.bind("<Button-1>", lambda event: self.jump(), add="+")
        canvas.configure(cursor="hand2")
        self._frame()

    def jump(self):
        self.jump_started = time.perf_counter()

    def _frame(self):
        if not self.canvas.winfo_exists():
            return
        if self.canvas.winfo_viewable():
            now = time.perf_counter()
            offset = round(2.5 * math.sin(now * 3.0))        # the gentle bob
            if self.jump_started is not None:
                t = (now - self.jump_started) / 0.5           # a 0.5 s jump
                if t >= 1.0:
                    self.jump_started = None
                else:
                    offset = -round(18 * math.sin(math.pi * t))
            # Only draw again when Suggy has actually moved.
            if offset != self.last_offset or self.redraw:
                self.last_offset = offset
                self.redraw = False
                self.draw(offset)
        self.canvas.after(FRAME_MS, self._frame)


# ---------------------------------------------------------------------------
# The banner at the top of the window
# ---------------------------------------------------------------------------

class Header:
    """
    The banner: a small Suggy on the left (wearing its cosmetics), the
    title in the middle and the points on the right. The points count
    up, and a star pops when they grow.
    """

    WIDTH, HEIGHT = 500, 72

    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT,
                                bg=PINK, highlightthickness=0)
        self.canvas.pack(fill="x")
        c = self.canvas
        c.create_text(98, 26, anchor="w", text="Companion app",
                      font=("Arial", 17, "bold"), fill="white")
        c.create_text(98, 49, anchor="w", fill="#ffe3e0",
                      text="For a parent or guardian, together with "
                           "their child", font=("Arial", 9))
        # The points "pill" on the right.
        c.create_oval(372, 18, 408, 54, fill="white", outline="", tags="pill")
        c.create_oval(452, 18, 488, 54, fill="white", outline="", tags="pill")
        c.create_rectangle(390, 18, 470, 54, fill="white", outline="",
                           tags="pill")
        # "\u2605" is a star character.
        self.star = c.create_text(394, 36, text="\u2605", fill=ORANGE,
                                  font=("Arial", 16), tags="pill")
        self.points_text = c.create_text(440, 36, text="", fill=INK,
                                         font=("Arial", 13, "bold"),
                                         tags="pill")
        self.points = None           # the number we are showing
        self.target = None
        self.pop_started = None
        self.accessories = []
        self.awake = True
        self.visible = False         # the points only show once linked
        self.bouncer = Bouncer(c, self._draw_suggy)
        self._set_pill(False)

    def _set_pill(self, visible):
        self.visible = visible
        self.canvas.itemconfigure("pill",
                                  state="normal" if visible else "hidden")

    def _draw_suggy(self, offset):
        c = self.canvas
        c.delete("suggy")
        before = set(c.find_all())
        # A soft green circle behind Suggy, like the keychain's screen.
        c.create_oval(12, 2, 80, 70, fill=pet_drawing.SCREEN_BG, outline="")
        pet_drawing.draw_pet(c, 48, 35 + offset,
                             "happy" if self.awake else "sleepy",
                             accessories=self.accessories)
        for item in set(c.find_all()) - before:
            c.addtag_withtag("suggy", item)

    def refresh(self, state):
        """Called every second by main.py with the newest data."""
        pet = state["pet"]
        if pet["accessories"] != self.accessories or pet["awake"] != self.awake:
            self.accessories = list(pet["accessories"])
            self.awake = pet["awake"]
            self.bouncer.redraw = True
        linked = state["link"]["linked"]
        if linked != self.visible:
            self._set_pill(linked)
        balance = state["points"]["balance"]
        if self.points is None:
            self.points = self.target = balance
            self.canvas.itemconfigure(self.points_text, text=str(balance))
        elif balance != self.target:
            if balance > self.target:
                self.pop_started = time.perf_counter()    # the star pops
                self.bouncer.jump()                       # and Suggy jumps
            self.target = balance
            self._count()

    def _count(self):
        """Count the points towards the target, a few at a time."""
        gap = self.target - self.points
        if gap == 0:
            return
        step = max(1, abs(gap) // 6)
        self.points += step if gap > 0 else -step
        self.canvas.itemconfigure(self.points_text, text=str(self.points))
        # The star grows and shrinks back while the points count up.
        size = 16
        if self.pop_started is not None:
            t = (time.perf_counter() - self.pop_started) / 0.6
            if t < 1.0:
                size = 16 + round(10 * math.sin(math.pi * t))
            else:
                self.pop_started = None
        self.canvas.itemconfigure(self.star, font=("Arial", size))
        if self.points != self.target:
            self.canvas.after(FRAME_MS, self._count)
        else:
            self.canvas.itemconfigure(self.star, font=("Arial", 16))
            self.pop_started = None


# ---------------------------------------------------------------------------
# The celebration pop-up
# ---------------------------------------------------------------------------

_showing = {"card": None}       # the celebration card on screen, if any


def celebrate(widget, title, subtitle="", accessories=()):
    """
    Show a happy card in the middle of the window for about 2 seconds:
    falling confetti, a jumping Suggy, a big title (e.g. "+10 points!")
    and a smaller line under it. A click closes it early.

    widget can be any widget of the app; the card is placed over its
    window.
    """
    root = widget.winfo_toplevel()
    if _showing["card"] is not None and _showing["card"].winfo_exists():
        _showing["card"].destroy()          # only one card at a time

    width, height = 340, 230
    card = tk.Canvas(root, width=width, height=height, bg=CARD,
                     highlightthickness=3, highlightbackground=ORANGE,
                     cursor="hand2")
    card.place(relx=0.5, rely=0.45, anchor="center")
    _showing["card"] = card
    card.bind("<Button-1>", lambda event: card.destroy())

    # The confetti: each piece is [canvas item, x, y, speed, sway, size].
    pieces = []
    for _ in range(36):
        x = random.uniform(0, width)
        y = random.uniform(-height, 0)
        size = random.choice((5, 6, 8))
        item = card.create_rectangle(x, y, x + size, y + size, outline="",
                                     fill=random.choice(CONFETTI_COLOURS))
        pieces.append([item, x, y, random.uniform(2.5, 5.0),
                       random.uniform(0, 6.28), size])

    card.create_text(width // 2, 150, text=title, fill=PINK,
                     font=("Arial", 22, "bold"))
    card.create_text(width // 2, 186, text=subtitle, fill=INK,
                     font=("Arial", 11), width=width - 30, justify="center")
    started = time.perf_counter()

    def frame():
        if not card.winfo_exists():
            return
        elapsed = time.perf_counter() - started
        if elapsed > 2.2:
            card.destroy()
            return
        # Confetti falls and sways a little from side to side.
        for piece in pieces:
            item, x, y, speed, sway, size = piece
            y += speed
            if y > height:
                y = -size
            piece[2] = y
            sx = x + 6 * math.sin(sway + elapsed * 4)
            card.coords(item, sx, y, sx + size, y + size)
        # Suggy jumps up and down.
        card.delete("suggy")
        before = set(card.find_all())
        jump = abs(math.sin(elapsed * 7)) * 16
        card.create_oval(width // 2 - 42, 28, width // 2 + 42, 112,
                         fill=pet_drawing.SCREEN_BG, outline="")
        pet_drawing.draw_pet(card, width // 2 + 2, 78 - jump, "happy",
                             mouth_open=True, accessories=accessories)
        for item in set(card.find_all()) - before:
            card.addtag_withtag("suggy", item)
        card.after(FRAME_MS, frame)

    frame()
