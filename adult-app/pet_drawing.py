"""
pet_drawing.py - draws Suggy and the food pictures with Canvas shapes.

Suggy is a little KIDNEY, like the keychain itself: a bean shape with a
dent on one side, a face and two small feet. It is drawn in the screen's
dark ink colour so it looks like part of the LCD.

Moods:
    happy  - smiling eyes (^ ^) and a smile
    okay   - dot eyes and a flat mouth (the smile is gone)
    sad    - dot eyes and a little frown
    hungry - big round eyes, small "o" mouth and a "?" bubble
    sleepy - closed eyes and "z Z"
mouth_open=True is used for the eating animation.

Also here: the small food pictures for the feeding cards.
"""

# The LCD colours (the same values as in keychain_frame.py). They are
# written here so this file needs no other file. An IDENTICAL copy of
# this file lives in adult-app/, so the app can draw Suggy too. If you
# change one copy, copy it over the other.
SCREEN_BG = "#c9e4a6"
SCREEN_INK = "#2f4a2f"


# A softer green than the ink, for the "tired" patches.
SOFT_INK = "#7f9a6c"


def _sore_patch(c, x1, y1, x2, y2):
    """
    A gentle "tired" mark: a pale patch with a few soft stripes.
    Used on the body parts that are tired after too much sugar.
    """
    c.create_oval(x1, y1, x2, y2, fill=SCREEN_BG, outline=SOFT_INK)
    step = 5
    for x in range(int(x1) + 3, int(x2) - 2, step):
        c.create_line(x, y2 - 3, x + 3, y1 + 3, fill=SOFT_INK)


def draw_pet(canvas, cx, cy, mood="happy", mouth_open=False, accessories=(),
             sore=()):
    """
    Draw Suggy the kidney centred at (cx, cy). About 60 x 55 pixels.
    accessories: the cosmetics Suggy is wearing, e.g. ["cap", "bow"].
    sore: body parts that look tired (a pale patch), from "eyes", "hands", "legs"
          and "kidney" (see feeding.sore_parts).
    """
    c = canvas
    ink = SCREEN_INK

    # Feet (drawn before the body so the body overlaps them)
    if "legs" in sore:
        _sore_patch(c, cx - 17, cy + 16, cx - 4, cy + 28)
        _sore_patch(c, cx + 1, cy + 16, cx + 14, cy + 28)
    else:
        c.create_oval(cx - 16, cy + 17, cx - 5, cy + 27, fill=ink, outline=ink)
        c.create_oval(cx + 2, cy + 17, cx + 13, cy + 27, fill=ink, outline=ink)

    # Little hands, one on each side
    if "hands" in sore:
        _sore_patch(c, cx - 34, cy + 1, cx - 21, cy + 13)
        _sore_patch(c, cx + 19, cy + 6, cx + 32, cy + 18)
    else:
        c.create_oval(cx - 33, cy + 2, cx - 22, cy + 12, fill=SCREEN_BG,
                      outline=ink, width=2)
        c.create_oval(cx + 20, cy + 7, cx + 31, cy + 17, fill=SCREEN_BG,
                      outline=ink, width=2)

    # Kidney body: a bean shape with a dent on the right side.
    # smooth=True makes Tkinter round the corners between these points.
    outline = [(-4, -27), (12, -26), (24, -16), (22, -5), (11, 0),
               (22, 6), (24, 15), (12, 24), (-6, 24), (-21, 15),
               (-26, -1), (-21, -17)]
    points = []
    for dx, dy in outline:
        points += [cx + dx, cy + dy]
    c.create_polygon(points, smooth=True, fill=SCREEN_BG, outline=ink,
                     width=3)

    # The face sits a little to the left, away from the dent.
    kidney_cx = cx
    cx = cx - 4

    # A sore mark low on the kidney body itself
    if "kidney" in sore:
        _sore_patch(c, cx - 8, cy + 11, cx + 10, cy + 21)

    # Rosy cheeks (small outlined circles)
    c.create_oval(cx - 17, cy + 1, cx - 12, cy + 6, outline=ink)
    c.create_oval(cx + 11, cy + 1, cx + 16, cy + 6, outline=ink)

    # Sore marks round the eyes (drawn first, the eyes go on top)
    if "eyes" in sore:
        _sore_patch(c, cx - 16, cy - 13, cx - 1, cy)
        _sore_patch(c, cx + 1, cy - 13, cx + 16, cy)

    # ---- Eyes ----
    if mood == "tired":
        # Droopy eyes: lids drawn as lines with a small dot under each
        c.create_line(cx - 13, cy - 8, cx - 4, cy - 6, fill=ink, width=2)
        c.create_line(cx + 4, cy - 6, cx + 13, cy - 8, fill=ink, width=2)
        c.create_oval(cx - 10, cy - 5, cx - 6, cy - 2, fill=ink, outline=ink)
        c.create_oval(cx + 6, cy - 5, cx + 10, cy - 2, fill=ink, outline=ink)
    elif mood == "sleepy":
        # Closed eyes: two short lines
        c.create_line(cx - 12, cy - 6, cx - 5, cy - 6, fill=ink, width=2)
        c.create_line(cx + 5, cy - 6, cx + 12, cy - 6, fill=ink, width=2)
    elif mood == "hungry":
        # Big round eyes
        c.create_oval(cx - 12, cy - 10, cx - 5, cy - 3, fill=ink, outline=ink)
        c.create_oval(cx + 5, cy - 10, cx + 12, cy - 3, fill=ink, outline=ink)
    elif mood in ("okay", "sad"):
        # Plain dot eyes: the smiling eyes are gone
        c.create_oval(cx - 11, cy - 9, cx - 6, cy - 4, fill=ink, outline=ink)
        c.create_oval(cx + 6, cy - 9, cx + 11, cy - 4, fill=ink, outline=ink)
    else:
        # Happy "^ ^" eyes, drawn as small arcs
        c.create_arc(cx - 13, cy - 10, cx - 4, cy - 2, start=0, extent=180,
                     style="arc", outline=ink, width=2)
        c.create_arc(cx + 4, cy - 10, cx + 13, cy - 2, start=0, extent=180,
                     style="arc", outline=ink, width=2)

    # ---- Mouth ----
    if mouth_open:
        # Wide open for eating
        c.create_oval(cx - 6, cy + 1, cx + 6, cy + 12, fill=ink, outline=ink)
    elif mood == "hungry":
        c.create_oval(cx - 3, cy + 3, cx + 3, cy + 9, outline=ink, width=2)
    elif mood in ("sleepy", "tired"):
        c.create_line(cx - 3, cy + 6, cx + 3, cy + 6, fill=ink, width=2)
    elif mood == "okay":
        # Flat mouth
        c.create_line(cx - 5, cy + 6, cx + 5, cy + 6, fill=ink, width=2)
    elif mood == "sad":
        # A little frown (an upside-down smile)
        c.create_arc(cx - 6, cy + 3, cx + 6, cy + 14, start=20, extent=140,
                     style="arc", outline=ink, width=2)
    else:
        # Smile
        c.create_arc(cx - 6, cy - 2, cx + 6, cy + 9, start=200, extent=140,
                     style="arc", outline=ink, width=2)

    cx = kidney_cx
    draw_accessories(c, cx - 2, cy - 3, accessories)

    # ---- Little extras that show the mood ----
    if mood == "sleepy":
        c.create_text(cx + 28, cy - 22, text="z", font=("Courier", 9, "bold"),
                      fill=ink)
        c.create_text(cx + 36, cy - 30, text="Z", font=("Courier", 11, "bold"),
                      fill=ink)
    elif mood == "hungry" and not mouth_open:
        # Thought bubble with a "?"
        c.create_oval(cx + 24, cy - 36, cx + 42, cy - 20, outline=ink, width=2)
        c.create_oval(cx + 22, cy - 18, cx + 26, cy - 14, fill=ink, outline=ink)
        c.create_text(cx + 33, cy - 28, text="?", font=("Courier", 10, "bold"),
                      fill=ink)


def draw_food_bite(canvas, x, y, size):
    """
    A simple round food piece used in the eating animation.
    It gets smaller each frame as Suggy eats it.
    """
    if size <= 0:
        return
    canvas.create_oval(x - size, y - size, x + size, y + size,
                       fill=SCREEN_INK, outline=SCREEN_INK)


def draw_hearts(canvas, x, y, hearts, max_hearts=5):
    """
    Suggy's health hearts in a row, starting at (x, y).
    Full hearts are filled in, empty hearts are just outlines.
    Each heart is two small circles on top of a triangle.
    """
    for i in range(max_hearts):
        hx = x + i * 11
        full = i < hearts
        fill = SCREEN_INK if full else ""
        canvas.create_oval(hx, y, hx + 5, y + 5, fill=fill, outline=SCREEN_INK)
        canvas.create_oval(hx + 4, y, hx + 9, y + 5, fill=fill,
                           outline=SCREEN_INK)
        canvas.create_polygon(hx, y + 3, hx + 9, y + 3, hx + 4.5, y + 9,
                              fill=fill, outline=SCREEN_INK)


def draw_accessories(canvas, cx, cy, accessories):
    """
    Draw each cosmetic Suggy is wearing (positions match draw_pet).
    The ids here must match the ids in adult-app/shop.py.
    Three groups: head, eyes and neck. Suggy wears one of each at most.
    """
    c = canvas
    ink = SCREEN_INK
    bg = SCREEN_BG

    # ---- Neck (drawn first, low on the body) ----
    if "scarf" in accessories:
        # A band round the bottom of the body with a hanging end
        c.create_rectangle(cx - 20, cy + 9, cx + 20, cy + 14, fill=ink,
                           outline=ink)
        c.create_rectangle(cx + 8, cy + 14, cx + 13, cy + 22, fill=ink,
                           outline=ink)
    if "bow_tie" in accessories:
        tx, ty = cx - 2, cy + 17
        c.create_polygon(tx - 9, ty - 5, tx, ty, tx - 9, ty + 5, fill=ink)
        c.create_polygon(tx + 9, ty - 5, tx, ty, tx + 9, ty + 5, fill=ink)
        c.create_oval(tx - 2, ty - 2, tx + 2, ty + 2, fill=bg, outline=ink)
    if "necktie" in accessories:
        tx, ty = cx - 2, cy + 13
        c.create_polygon(tx - 3, ty, tx + 3, ty, tx + 2, ty + 4, tx - 2,
                         ty + 4, fill=ink)                          # knot
        c.create_polygon(tx - 2, ty + 4, tx + 2, ty + 4, tx + 4, ty + 13,
                         tx, ty + 17, tx - 4, ty + 13, fill=ink)    # blade
    if "necklace" in accessories:
        # A curve of beads
        for dx, dy in ((-14, 12), (-9, 16), (-3, 18), (3, 18), (9, 16),
                       (14, 12)):
            c.create_oval(cx - 2 + dx - 2, cy + dy - 2, cx - 2 + dx + 2,
                          cy + dy + 2, fill=ink, outline=ink)
    if "medal" in accessories:
        # A ribbon in a V with a round medal at the bottom
        c.create_line(cx - 12, cy + 9, cx - 2, cy + 17, fill=ink, width=2)
        c.create_line(cx + 8, cy + 9, cx - 2, cy + 17, fill=ink, width=2)
        c.create_oval(cx - 7, cy + 15, cx + 3, cy + 25, fill=bg, outline=ink,
                      width=2)
        c.create_line(cx - 2, cy + 18, cx - 2, cy + 22, fill=ink, width=2)

    # ---- Eyes ----
    if "glasses" in accessories:
        c.create_oval(cx - 15, cy - 12, cx - 3, cy, outline=ink, width=2)
        c.create_oval(cx + 3, cy - 12, cx + 15, cy, outline=ink, width=2)
        c.create_line(cx - 3, cy - 6, cx + 3, cy - 6, fill=ink, width=2)
    if "sunglasses" in accessories:
        c.create_oval(cx - 16, cy - 12, cx - 3, cy, fill=ink, outline=ink)
        c.create_oval(cx + 3, cy - 12, cx + 16, cy, fill=ink, outline=ink)
        c.create_line(cx - 3, cy - 8, cx + 3, cy - 8, fill=ink, width=2)
        c.create_line(cx - 16, cy - 8, cx - 22, cy - 10, fill=ink, width=2)
    if "square_glasses" in accessories:
        c.create_rectangle(cx - 15, cy - 12, cx - 3, cy - 1, outline=ink,
                           width=2)
        c.create_rectangle(cx + 3, cy - 12, cx + 15, cy - 1, outline=ink,
                           width=2)
        c.create_line(cx - 3, cy - 7, cx + 3, cy - 7, fill=ink, width=2)
    if "monocle" in accessories:
        c.create_oval(cx + 2, cy - 13, cx + 16, cy + 1, outline=ink, width=2)
        c.create_line(cx + 14, cy - 1, cx + 17, cy + 6, cx + 14, cy + 13,
                      fill=ink, smooth=True)                        # chain
    if "goggles" in accessories:
        c.create_line(cx - 24, cy - 7, cx + 22, cy - 7, fill=ink, width=3)
        c.create_oval(cx - 17, cy - 14, cx - 1, cy + 2, fill=bg, outline=ink,
                      width=3)
        c.create_oval(cx + 1, cy - 14, cx + 17, cy + 2, fill=bg, outline=ink,
                      width=3)
        c.create_oval(cx - 11, cy - 8, cx - 7, cy - 4, fill=ink, outline=ink)
        c.create_oval(cx + 7, cy - 8, cx + 11, cy - 4, fill=ink, outline=ink)

    # ---- Head ----
    if "cap" in accessories:
        # Rounded cap top plus a brim sticking out to the right
        c.create_arc(cx - 18, cy - 30, cx + 10, cy - 10, start=0, extent=180,
                     style="pieslice", fill=ink, outline=ink)
        c.create_line(cx + 6, cy - 20, cx + 22, cy - 20, fill=ink, width=3)
    if "beanie" in accessories:
        # A dome, a folded band and a pom-pom on top
        c.create_arc(cx - 19, cy - 36, cx + 15, cy - 6, start=0, extent=180,
                     style="pieslice", fill=ink, outline=ink)
        c.create_rectangle(cx - 20, cy - 24, cx + 16, cy - 19, fill=bg,
                           outline=ink, width=2)
        c.create_oval(cx - 6, cy - 43, cx + 2, cy - 35, fill=bg, outline=ink,
                      width=2)
    if "top_hat" in accessories:
        c.create_rectangle(cx - 13, cy - 44, cx + 9, cy - 22, fill=ink,
                           outline=ink)
        c.create_line(cx - 13, cy - 27, cx + 9, cy - 27, fill=bg, width=2)
        c.create_line(cx - 21, cy - 21, cx + 17, cy - 21, fill=ink, width=4)
    if "bow" in accessories:
        # Two small triangles meeting at a knot, on the left of the head
        bx, by = cx - 20, cy - 16
        c.create_polygon(bx - 7, by - 5, bx, by, bx - 7, by + 5, fill=ink)
        c.create_polygon(bx + 7, by - 5, bx, by, bx + 7, by + 5, fill=ink)
        c.create_oval(bx - 2, by - 2, bx + 2, by + 2, fill=bg, outline=ink)
    if "crown" in accessories:
        top = cy - 44
        c.create_polygon(cx - 10, top + 10, cx - 10, top, cx - 5, top + 5,
                         cx, top, cx + 5, top + 5, cx + 10, top,
                         cx + 10, top + 10, fill=ink, outline=ink)


# ---------------------------------------------------------------------------
# Food pictures for the feeding cards. Each is about 36 x 32 pixels,
# centred at (x, y), drawn only with simple Canvas shapes.
# ---------------------------------------------------------------------------

def _bowl(c, x, y, topping=None):
    """A bowl with a heap in it. topping: None, "grains", "rings", "flakes"."""
    ink = SCREEN_INK
    c.create_arc(x - 15, y - 16, x + 15, y + 10, start=0, extent=180,
                 style="chord", fill=SCREEN_BG, outline=ink, width=2)
    spots = ((-8, -6), (-2, -10), (4, -7), (9, -4), (-5, -3), (1, -4),
             (-10, -2), (6, -11), (-1, -7))
    for dx, dy in spots:
        if topping == "grains":          # short dark grains
            c.create_line(x + dx, y + dy, x + dx + 3, y + dy + 1,
                          fill=ink, width=2)
        elif topping == "flakes":        # small dots
            c.create_oval(x + dx, y + dy, x + dx + 2, y + dy + 2,
                          fill=ink, outline=ink)
    if topping == "rings":               # little cereal rings
        for dx, dy in ((-9, -6), (-1, -11), (6, -6), (-3, -4)):
            c.create_oval(x + dx, y + dy, x + dx + 6, y + dy + 5,
                          outline=ink, width=2)
    c.create_arc(x - 18, y - 22, x + 18, y + 14, start=180, extent=180,
                 style="chord", fill=ink, outline=ink)


def _glass(c, x, y, full=False):
    """A glass, wider at the top. full=True fills it with a dark drink."""
    ink = SCREEN_INK
    c.create_polygon(x - 11, y - 15, x + 11, y - 15, x + 8, y + 15,
                     x - 8, y + 15, fill=SCREEN_BG, outline=ink, width=2)
    if full:
        c.create_polygon(x - 10, y - 8, x + 10, y - 8, x + 8, y + 15,
                         x - 8, y + 15, fill=ink, outline=ink)
    else:
        c.create_line(x - 10, y - 8, x + 10, y - 8, fill=ink, width=2)


def _bread(c, x, y, speckled=False):
    """A slice of bread. speckled=True adds the grains of wholemeal."""
    ink = SCREEN_INK
    c.create_oval(x - 15, y - 16, x + 15, y + 2, fill=SCREEN_BG,
                  outline=ink, width=2)
    c.create_rectangle(x - 11, y - 6, x + 11, y + 15, fill=SCREEN_BG,
                       outline=ink, width=2)
    c.create_rectangle(x - 9, y - 8, x + 9, y - 3, fill=SCREEN_BG, outline="")
    if speckled:
        for dx, dy in ((-6, -9), (3, -11), (7, -3), (-4, 0), (2, 5),
                       (-7, 8), (6, 10), (0, -4)):
            c.create_oval(x + dx, y + dy, x + dx + 2, y + dy + 2,
                          fill=ink, outline=ink)


def draw_food_icon(canvas, x, y, food_id):
    """Draw the picture for one food id from feeding.py."""
    c = canvas
    ink = SCREEN_INK
    bg = SCREEN_BG
    # ---- Meals ----
    if food_id == "white_rice":
        _bowl(c, x, y)
    elif food_id == "brown_rice":
        _bowl(c, x, y, "grains")
    elif food_id == "sweet_cereal":
        _bowl(c, x, y, "rings")
    elif food_id == "oats":
        _bowl(c, x, y, "flakes")
    elif food_id == "white_bread":
        _bread(c, x, y)
    elif food_id == "wholemeal_bread":
        _bread(c, x, y, speckled=True)
    # ---- Drinks ----
    elif food_id == "sweet_drink":
        _glass(c, x, y, full=True)
        c.create_line(x + 3, y - 6, x + 9, y - 22, fill=ink, width=2)  # straw
    elif food_id == "water":
        _glass(c, x, y)
        c.create_oval(x - 3, y + 1, x + 3, y + 7, outline=ink, width=2)
    elif food_id == "fruit_juice":
        _glass(c, x, y, full=True)
        # a slice of fruit on the rim
        c.create_oval(x + 4, y - 23, x + 16, y - 11, fill=bg, outline=ink,
                      width=2)
        c.create_line(x + 10, y - 22, x + 10, y - 12, fill=ink)
        c.create_line(x + 5, y - 17, x + 15, y - 17, fill=ink)
    elif food_id == "bubble_tea":
        _glass(c, x, y, full=True)
        c.create_line(x + 2, y - 4, x + 7, y - 23, fill=ink, width=4)  # wide straw
        for dx, dy in ((-5, 8), (0, 10), (5, 8), (-2, 4), (3, 4)):
            c.create_oval(x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2,
                          fill=bg, outline=bg)                        # pearls
    elif food_id == "plain_tea":
        # A cup with a handle and a little steam.
        c.create_rectangle(x - 13, y - 4, x + 7, y + 13, fill=bg,
                           outline=ink, width=2)
        c.create_arc(x + 2, y - 1, x + 15, y + 10, start=270, extent=180,
                     style="arc", outline=ink, width=2)
        c.create_line(x - 7, y - 9, x - 5, y - 13, x - 7, y - 17, fill=ink,
                      width=2, smooth=True)
        c.create_line(x + 1, y - 9, x + 3, y - 13, x + 1, y - 17, fill=ink,
                      width=2, smooth=True)
    elif food_id == "plain_milk":
        # A milk carton.
        c.create_rectangle(x - 9, y - 8, x + 9, y + 15, fill=bg, outline=ink,
                           width=2)
        c.create_polygon(x - 9, y - 8, x, y - 18, x + 9, y - 8, fill=bg,
                         outline=ink, width=2)
        c.create_line(x - 5, y + 2, x + 5, y + 2, fill=ink, width=2)
    # ---- Desserts ----
    elif food_id == "ice_cream":
        # Two scoops on a cone.
        c.create_polygon(x - 9, y, x + 9, y, x, y + 17, fill=bg,
                         outline=ink, width=2)
        c.create_oval(x - 10, y - 12, x + 10, y + 4, fill=ink, outline=ink)
        c.create_oval(x - 7, y - 21, x + 7, y - 8, fill=bg, outline=ink,
                      width=2)
    elif food_id == "apple":
        c.create_oval(x - 13, y - 9, x + 3, y + 14, fill=bg, outline=ink,
                      width=2)
        c.create_oval(x - 3, y - 9, x + 13, y + 14, fill=bg, outline=ink,
                      width=2)
        c.create_rectangle(x - 4, y - 5, x + 4, y + 11, fill=bg, outline="")
        c.create_line(x, y - 8, x + 2, y - 16, fill=ink, width=2)   # stem
        c.create_oval(x + 3, y - 18, x + 11, y - 12, fill=ink, outline=ink)
    elif food_id == "donut":
        c.create_oval(x - 16, y - 13, x + 16, y + 13, fill=ink, outline=ink)
        c.create_oval(x - 5, y - 4, x + 5, y + 4, fill=bg, outline=bg)
        for dx, dy in ((-10, -5), (8, -6), (-9, 5), (9, 5), (0, -9)):
            c.create_line(x + dx, y + dy, x + dx + 3, y + dy + 1, fill=bg,
                          width=2)                                   # sprinkles
    elif food_id == "banana":
        c.create_arc(x - 16, y - 26, x + 16, y + 10, start=200, extent=140,
                     style="arc", outline=ink, width=8)
        c.create_line(x + 13, y - 6, x + 16, y - 12, fill=ink, width=3)
    elif food_id == "sweet_cake":
        # A slice of layer cake with a cherry on top.
        c.create_polygon(x - 15, y + 13, x + 15, y + 13, x + 15, y - 8,
                         x - 15, y, fill=bg, outline=ink, width=2)
        c.create_line(x - 15, y + 6, x + 15, y + 3, fill=ink, width=3)
        c.create_oval(x + 4, y - 17, x + 12, y - 9, fill=ink, outline=ink)
    elif food_id == "plain_nuts":
        for dx, dy in ((-9, -4), (5, -8), (-1, 6)):
            c.create_oval(x + dx - 7, y + dy - 5, x + dx + 7, y + dy + 5,
                          fill=bg, outline=ink, width=2)
            c.create_line(x + dx - 4, y + dy, x + dx + 4, y + dy, fill=ink)


def draw_bell(canvas, x, y):
    """A ringing bell, the picture for the insulin reminder."""
    c = canvas
    ink = SCREEN_INK
    c.create_oval(x - 11, y - 14, x + 11, y + 8, fill=ink, outline=ink)
    c.create_rectangle(x - 11, y - 3, x + 11, y + 8, fill=ink, outline=ink)
    c.create_polygon(x - 16, y + 10, x + 16, y + 10, x + 11, y + 2,
                     x - 11, y + 2, fill=ink, outline=ink)        # the rim
    c.create_oval(x - 4, y + 9, x + 4, y + 16, fill=ink, outline=ink)
    c.create_line(x, y - 18, x, y - 13, fill=ink, width=3)        # the top
    # Little "ringing" lines on both sides.
    c.create_line(x - 20, y - 8, x - 16, y - 4, fill=ink, width=2)
    c.create_line(x + 20, y - 8, x + 16, y - 4, fill=ink, width=2)


def draw_heart_icon(canvas, x, y):
    """A big heart with a little cross, the picture for Check."""
    c = canvas
    ink = SCREEN_INK
    c.create_oval(x - 15, y - 13, x + 1, y + 3, fill=ink, outline=ink)
    c.create_oval(x - 1, y - 13, x + 15, y + 3, fill=ink, outline=ink)
    c.create_polygon(x - 14, y - 1, x + 14, y - 1, x, y + 15, fill=ink,
                     outline=ink)
    c.create_line(x - 5, y - 3, x + 5, y - 3, fill=SCREEN_BG, width=3)
    c.create_line(x, y - 8, x, y + 2, fill=SCREEN_BG, width=3)


def draw_sore_box(canvas, x1, y1, x2, y2):
    """The same soft "tired" mark as on Suggy, as a small box in a list."""
    canvas.create_rectangle(x1, y1, x2, y2, fill=SCREEN_BG,
                            outline=SOFT_INK)
    for x in range(int(x1) + 3, int(x2) - 2, 5):
        canvas.create_line(x, y2 - 3, x + 3, y1 + 3, fill=SOFT_INK)
