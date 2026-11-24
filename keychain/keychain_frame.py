"""
keychain_frame.py - shows the keychain as a 3D model you can turn around.

The shape is built in keychain_model.py. This file is a tiny 3D viewer
written with only Tkinter:

    - Drag the keychain with the mouse to turn it and see every side.
    - Let go near the back (or press "Turn around") and it settles on
      the BACK, where the live screen and the arrow and OK buttons are.
    - Let go near the front and it settles on the face.

How the 3D drawing works (the "painter's" method):
    1. Turn every corner point of the model by the current angles.
    2. Skip the faces that point away from us.
    3. Sort the rest from far to near.
    4. Draw them in that order as flat coloured shapes, a bit brighter
       when they face the light.

Keeping it smooth:
    - There are two copies of the model. A LIGHT one with few faces is
      drawn while the keychain is moving, and a DETAILED one as soon as
      it stops.
    - While you drag, a steady "frame loop" runs about 60 times a
      second. Each frame the keychain moves part of the way towards
      where your mouse asked it to be, so it glides instead of jumping.
      When you let go it keeps turning a little and slows down.
    - Animations are timed with the clock. On a slow computer they skip
      frames instead of getting slower.
    - All the shapes of one frame are sent to Tk in ONE go, which is
      faster than sending them one by one.

What appears ON the small screen is decided by the screen files.
"""

import math
import time
import tkinter as tk

import keychain_model

# ---- Sizes (in pixels) -----------------------------------------------------
WINDOW_WIDTH = 460
WINDOW_HEIGHT = 560

# The area the screen files draw on (their coordinates are 0..200, 0..160).
SCREEN_WIDTH = 200
SCREEN_HEIGHT = 160
# The screen widget is a little bigger, to leave room for the soft rim.
SCREEN_MARGIN = 6

SCALE = 110              # pixels for one unit of the 3D model
CENTRE_X = 230
CENTRE_Y = 312

# ---- Colours ---------------------------------------------------------------
BACKGROUND = "#f1eaf5"   # soft lilac behind the keychain
BEZEL_COLOR = "#f3cfab"  # the cream frame the screen sits in
BUTTON_COLOR = "#f5a623"
BUTTON_EDGE = "#d98c0f"
BUTTON_PRESSED = "#d98c0f"
BUTTON_HOVER = "#ffc24d"   # a button the mouse is resting on
# Pixel-screen colours (like an old LCD)
SCREEN_BG = "#c9e4a6"
SCREEN_INK = "#2f4a2f"
SCREEN_RIM = "#e7b592"         # soft edge between the frame and the screen
SCREEN_RIM_INNER = "#8fae78"   # thin darker-green edge of the glass

# The three buttons: a left arrow, OK, and a right arrow.
# The arrows move between choices and OK picks one. That is all.

# ---- Light -----------------------------------------------------------------
# Direction the light comes from (towards the viewer, up and a bit left).
LIGHT = (-0.37, 0.52, 0.79)
SHADES = 24      # how many brightness steps we prepare for each colour

BACK_ANGLE = 180.0     # yaw angle that shows the back
FRONT_ANGLE = 0.0      # yaw angle that shows the face

# ---- Movement ---------------------------------------------------------------
FRAME_MS = 16          # one frame of movement (about 60 frames a second)
FOLLOW = 0.35          # each frame, move this share of the way to the mouse
GLIDE = 0.90           # after letting go, the turning speed shrinks by this
MAX_GLIDE_SPEED = 14.0   # degrees per frame, so a wild flick stays calm
STILL_SECONDS = 0.25   # holding still this long draws the detailed model
TURN_MS_PER_STEP = 26  # turn_to(steps=16) takes about 0.4 seconds


def rounded_points(x1, y1, x2, y2, radius, steps=6):
    """Corner points of a rounded rectangle (a list of (x, y))."""
    points = []
    corners = ((x2 - radius, y1 + radius, -90), (x2 - radius, y2 - radius, 0),
               (x1 + radius, y2 - radius, 90), (x1 + radius, y1 + radius, 180))
    for cx, cy, start in corners:
        for i in range(steps + 1):
            a = math.radians(start + 90 * i / steps)
            points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return points


def shade_table(colour):
    """A list of SHADES versions of a '#rrggbb' colour, dark to bright."""
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    table = []
    for i in range(SHADES):
        k = 0.62 + 0.44 * i / (SHADES - 1)       # brightness 0.62 .. 1.06
        table.append("#%02x%02x%02x" % (min(255, int(r * k)),
                                        min(255, int(g * k)),
                                        min(255, int(b * k))))
    return table


class PreparedModel:
    """
    One copy of the model, laid out in flat lists so drawing is fast:
        points   every corner point (x, y, z)
        faces    for every face: (corner numbers, normal, shades, bias,
                 two opposite corners used to judge how far away it is)
    """

    def __init__(self, parts):
        self.points = []
        self.faces = []
        tables = {}
        for part in parts:
            offset = len(self.points)
            self.points.extend(part["points"])
            if part["colour"] not in tables:
                tables[part["colour"]] = shade_table(part["colour"])
            shades = tables[part["colour"]]
            for face in part["faces"]:
                corners = tuple(i + offset for i in face)
                normal = self._normal(corners)
                self.faces.append((corners, normal, shades, part["bias"],
                                   corners[0], corners[len(corners) // 2]))

    def _normal(self, corners):
        """The direction a face points in (length 1)."""
        n = len(corners)
        a = self.points[corners[0]]
        b = self.points[corners[n // 3]]
        c = self.points[corners[2 * n // 3]]
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        return nx / length, ny / length, nz / length


class KeychainFrame:
    """
    Builds the 3D keychain inside the given Tk window.

    on_button is a function we call with "LEFT", "OK", "RIGHT" or "HOME" when a button
    is pressed (by mouse click or by keyboard).
    """

    def __init__(self, root, on_button, ref_number="", intro_spin=True):
        self.on_button = on_button
        self.ref_number = ref_number

        self.canvas = tk.Canvas(
            root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
            bg=BACKGROUND, highlightthickness=0,
        )
        self.canvas.pack()

        # Two copies of the model: light for turning, detailed for still.
        self.light_model = PreparedModel(keychain_model.build_model(detail=1))
        self.detailed_model = PreparedModel(keychain_model.build_model(detail=2))
        length = math.sqrt(sum(v * v for v in LIGHT))
        self.light = tuple(v / length for v in LIGHT)

        # Current view: yaw = turning left/right, pitch = tilting up/down.
        self.yaw = FRONT_ANGLE if intro_spin else BACK_ANGLE
        self.pitch = 0.0
        self.docked = False          # True when settled on the back
        self.animating = False
        self.drag_from = None        # where the mouse went down
        self.dragged = False
        self.button_items = {}       # flat button circles (when docked)
        self.hover = None            # the button the mouse is resting on
        # Smooth turning (see the frame loop below).
        self.target_yaw = self.yaw   # where the mouse asked us to be
        self.target_pitch = self.pitch
        self.last_target_yaw = self.yaw
        self.glide_speed = 0.0       # degrees per frame after letting go
        self.loop_running = False
        self.dragging = False
        self.still_since = None      # when the view last stopped changing
        self.showing_detailed = False

        self.screen, self.screen_item = self._make_screen()

        self.canvas.bind("<ButtonPress-1>", self._mouse_down)
        self.canvas.bind("<B1-Motion>", self._mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self._mouse_up)
        self.canvas.bind("<Motion>", self._mouse_hover)
        self.canvas.bind("<Leave>", lambda event: self._set_hover(None))

        # Keyboard keys do the same as clicks:
        #   Left and Right arrow keys = the arrow buttons
        #   Enter or Space            = OK
        root.bind("<KeyPress-Left>", lambda event: self.press("LEFT"))
        root.bind("<KeyPress-Right>", lambda event: self.press("RIGHT"))
        for key in ("Return", "KP_Enter", "space"):
            root.bind("<KeyPress-%s>" % key, lambda event: self.press("OK"))
        #   H, Home or Esc            = the small Home button
        for key in ("h", "H", "Home", "Escape"):
            root.bind("<KeyPress-%s>" % key, lambda event: self.press("HOME"))

        if intro_spin:
            # Show the face for a moment, then spin round to the back.
            self.render(detailed=True)
            self.canvas.after(900, lambda: self.turn_to(BACK_ANGLE))
        else:
            self._dock()

    def _make_screen(self):
        """
        The live screen is its own small Canvas. It is only shown when the
        keychain is settled on its back. Its background is the same colour
        as the frame behind it, and the screen files draw a rounded glass
        shape on it, so it blends into the keychain with no hard corners.
        """
        width = SCREEN_WIDTH + 2 * SCREEN_MARGIN
        height = SCREEN_HEIGHT + 2 * SCREEN_MARGIN
        screen = tk.Canvas(self.canvas, width=width, height=height,
                           bg=BEZEL_COLOR, highlightthickness=0)
        # Make the widget's top-left corner be (-margin, -margin), so the
        # screen files can keep drawing from (0, 0) to (200, 160).
        screen.configure(scrollregion=(-SCREEN_MARGIN, -SCREEN_MARGIN,
                                       SCREEN_WIDTH + SCREEN_MARGIN,
                                       SCREEN_HEIGHT + SCREEN_MARGIN))
        x = CENTRE_X + keychain_model.SCREEN_CENTRE[0] * SCALE
        y = CENTRE_Y - keychain_model.SCREEN_CENTRE[1] * SCALE
        item = self.canvas.create_window(x, y, window=screen, state="hidden")
        return screen, item

    # ---- Drawing the 3D model ----------------------------------------------

    def render(self, detailed=False):
        """Draw the whole keychain at the current yaw and pitch."""
        model = self.detailed_model if detailed else self.light_model
        canvas = self.canvas

        # Rotation numbers: first turn (yaw, around the up axis), then
        # tilt (pitch, around the left-right axis).
        cy, sy = math.cos(math.radians(self.yaw)), math.sin(math.radians(self.yaw))
        cp, sp = math.cos(math.radians(self.pitch)), math.sin(math.radians(self.pitch))
        # Turning a point (x, y, z) gives:
        #   across = cy*x + sy*z
        #   up     = sp*sy*x + cp*y - sp*cy*z
        #   near   = -cp*sy*x + sp*y + cp*cy*z
        ax, az = cy * SCALE, sy * SCALE
        ux, uy, uz = sp * sy * SCALE, cp * SCALE, -sp * cy * SCALE
        nx_, ny_, nz_ = -cp * sy, sp, cp * cy

        # 1. Turn every point, and work out its place on the canvas.
        #    The place is kept as text ("x y"), ready to hand to Tk.
        pxy, pz = [], []
        for x, y, z in model.points:
            pxy.append("%d %d" % (CENTRE_X + ax * x + az * z,
                                  CENTRE_Y - (ux * x + uy * y + uz * z)))
            pz.append(nx_ * x + ny_ * y + nz_ * z)

        # The light, turned the opposite way, so we can compare it with
        # each face without turning the faces themselves.
        lx, ly, lz = self.light
        mlx = cy * lx + sp * sy * ly - cp * sy * lz
        mly = cp * ly + sp * lz
        mlz = sy * lx - sp * cy * ly + cp * cy * lz
        top = SHADES - 1

        # 2. Keep only the faces pointing at us, and pick their brightness.
        to_draw = []
        for corners, (fx, fy, fz), shades, bias, first, opposite in model.faces:
            if nx_ * fx + ny_ * fy + nz_ * fz <= 0:
                continue                      # points away: skip it
            light = fx * mlx + fy * mly + fz * mlz
            colour = shades[int(top * light)] if light > 0 else shades[0]
            to_draw.append(((pz[first] + pz[opposite]) * 0.5 + bias,
                            colour, corners))

        # 3. Far things first, so near things are painted over them.
        to_draw.sort(key=lambda item: item[0])

        # 4. Paint. We write ONE long list of Tk drawing commands and
        #    send it in a single call. That is quicker than calling
        #    canvas.create_polygon() a thousand times.
        name = str(canvas)
        commands = [name + " delete model"]
        for _depth, colour, corners in to_draw:
            commands.append("%s create polygon %s -fill %s -outline %s "
                            "-tags model"
                            % (name, " ".join([pxy[i] for i in corners]),
                               colour, colour))
        canvas.tk.eval("\n".join(commands))
        self.showing_detailed = detailed
        self.hover = None

        if self.docked:
            self._draw_back_details()
        else:
            canvas.create_text(8, 12, anchor="w",
                               text="Drag the keychain to turn it",
                               font=("Arial", 9), fill="#8a8377", tags="model")

    def _draw_back_details(self):
        """
        Flat, crisp details when settled on the back: the face of the
        cream frame, the arrow, OK and Home buttons, and the
        reference number.
        """
        canvas = self.canvas
        left, bottom, right, top = keychain_model.FRAME_BOX
        outline = rounded_points(
            CENTRE_X + left * SCALE, CENTRE_Y - top * SCALE,
            CENTRE_X + right * SCALE, CENTRE_Y - bottom * SCALE,
            keychain_model.FRAME_CORNER * SCALE)
        canvas.create_polygon([v for point in outline for v in point],
                              fill=BEZEL_COLOR, outline="#e3b48d", width=2,
                              tags="model")
        r = keychain_model.BUTTON_RADIUS * SCALE
        self.button_items = {}
        for label, (x, y) in keychain_model.BUTTON_SPOTS.items():
            bx, by = CENTRE_X + x * SCALE, CENTRE_Y - y * SCALE
            self.button_items[label] = canvas.create_oval(
                bx - r, by - r, bx + r, by + r, fill=BUTTON_COLOR,
                outline=BUTTON_EDGE, width=3, tags="model")
            # The arrows are drawn as triangles (no special font needed).
            if label == "LEFT":
                canvas.create_polygon(bx - 9, by, bx + 6, by - 9, bx + 6,
                                      by + 9, fill="#5b3a00", tags="model")
            elif label == "RIGHT":
                canvas.create_polygon(bx + 9, by, bx - 6, by - 9, bx - 6,
                                      by + 9, fill="#5b3a00", tags="model")
            else:
                canvas.create_text(bx, by, text="OK",
                                   font=("Arial", 12, "bold"), fill="#5b3a00",
                                   tags="model")
        # The small Home button above the screen, with a little house on it.
        hx, hy = self._home_xy()
        hr = keychain_model.HOME_RADIUS * SCALE
        self.button_items["HOME"] = canvas.create_oval(
            hx - hr, hy - hr, hx + hr, hy + hr, fill=BUTTON_COLOR,
            outline=BUTTON_EDGE, width=2, tags="model")
        canvas.create_polygon(hx - 6, hy, hx, hy - 6, hx + 6, hy,
                              fill="#5b3a00", tags="model")       # roof
        canvas.create_rectangle(hx - 4, hy, hx + 4, hy + 5, fill="#5b3a00",
                                outline="", tags="model")         # walls
        canvas.create_text(CENTRE_X, CENTRE_Y + 1.64 * SCALE,
                           text="REF " + self.ref_number,
                           font=("Courier", 9, "bold"), fill="#7a2733",
                           tags="model")

    def _home_xy(self):
        """Where the Home button is in the window (when on the back)."""
        x, y = keychain_model.HOME_SPOT
        return CENTRE_X + x * SCALE, CENTRE_Y - y * SCALE

    # ---- Settling on the back, and turning ----------------------------------

    def _dock(self):
        """Settle exactly on the back and show the live screen."""
        self.yaw, self.pitch = BACK_ANGLE, 0.0
        self.target_yaw, self.target_pitch = self.yaw, self.pitch
        self.docked = True
        self.render(detailed=True)
        self.canvas.itemconfigure(self.screen_item, state="normal")

    def _undock(self):
        """Hide the live screen so the model can turn freely."""
        self.docked = False
        self.canvas.configure(cursor="")
        self.canvas.itemconfigure(self.screen_item, state="hidden")

    def turn_to(self, target_yaw, steps=16):
        """
        Smoothly turn to the back or the front. The turn always takes
        the same time (steps x 26 ms): a slow computer shows fewer
        frames, not a slower turn.
        """
        if self.animating:
            return
        self._undock()
        self.animating = True
        self.glide_speed = 0.0
        # Take the short way round.
        start_yaw = self.yaw % 360
        difference = (target_yaw - start_yaw + 180) % 360 - 180
        start_pitch = self.pitch
        duration = steps * TURN_MS_PER_STEP / 1000.0
        started = time.perf_counter()

        def frame():
            t = min(1.0, (time.perf_counter() - started) / duration)
            ease = t * t * (3 - 2 * t)           # start and stop gently
            self.yaw = start_yaw + difference * ease
            self.pitch = start_pitch * (1 - ease)
            if t < 1.0:
                self.render()
                self.canvas.after(FRAME_MS, frame)
            else:
                self.animating = False
                self.yaw = target_yaw % 360
                self.pitch = 0.0
                self.target_yaw, self.target_pitch = self.yaw, self.pitch
                if target_yaw % 360 == BACK_ANGLE:
                    self._dock()
                else:
                    self.render(detailed=True)
        frame()

    def flip(self):
        """The "Turn around" button: back <-> face."""
        near_back = abs((self.yaw - BACK_ANGLE + 180) % 360 - 180) < 90
        self.turn_to(FRONT_ANGLE if near_back else BACK_ANGLE)

    # ---- Mouse: drag to turn, click to press buttons ------------------------

    def _mouse_down(self, event):
        self.drag_from = (event.x, event.y, self.yaw, self.pitch)
        self.dragged = False

    def _mouse_move(self, event):
        if self.drag_from is None or self.animating:
            return
        x0, y0, yaw0, pitch0 = self.drag_from
        dx, dy = event.x - x0, event.y - y0
        if not self.dragged and abs(dx) + abs(dy) < 6:
            return                      # tiny wobble: still counts as a click
        if not self.dragged:
            self.dragged = True
            self.dragging = True
            self._undock()
            self.target_yaw = self.last_target_yaw = self.yaw
            self.glide_speed = 0.0
        # Only remember where the mouse wants the keychain to be. The
        # frame loop does the drawing, at its own steady pace.
        self.target_yaw = yaw0 + dx * 0.6
        self.target_pitch = max(-70.0, min(70.0, pitch0 + dy * 0.5))
        if not self.loop_running:
            self.loop_running = True
            self._frame()

    def _frame(self):
        """
        One frame of smooth turning. Runs again and again (about 60
        times a second) while the keychain is being dragged or is still
        gliding, and stops by itself when everything is at rest.
        """
        if self.animating or self.docked:
            self.loop_running = False
            return
        frame_started = time.perf_counter()

        if self.dragging:
            # How fast is the mouse turning it? Remembered for the glide.
            moved = self.target_yaw - self.last_target_yaw
            self.glide_speed = 0.6 * self.glide_speed + 0.4 * moved
            self.last_target_yaw = self.target_yaw
        else:
            # Let go: keep turning a little, slower every frame.
            self.target_yaw += self.glide_speed
            self.glide_speed *= GLIDE

        # Move part of the way towards the target (this is the "glide").
        yaw_gap = self.target_yaw - self.yaw
        pitch_gap = self.target_pitch - self.pitch
        moving = abs(yaw_gap) > 0.2 or abs(pitch_gap) > 0.2
        if moving:
            self.yaw += yaw_gap * FOLLOW
            self.pitch += pitch_gap * FOLLOW
            self.render()                       # the light model
            self.still_since = None
        elif self.still_since is None:
            self.still_since = frame_started

        if not moving and not self.dragging and abs(self.glide_speed) < 0.2:
            # Everything is at rest: stop the loop and settle.
            self.loop_running = False
            self.yaw %= 360
            self._settle()
            return
        if (not moving and not self.showing_detailed
                and frame_started - self.still_since > STILL_SECONDS):
            self.render(detailed=True)          # held still: show the detail

        # Come back for the next frame, allowing for the time we used.
        used_ms = (time.perf_counter() - frame_started) * 1000
        self.canvas.after(max(1, int(FRAME_MS - used_ms)), self._frame)

    def _settle(self):
        """After a drag has come to rest: snap to the back or face if near."""
        off_back = abs((self.yaw - BACK_ANGLE + 180) % 360 - 180)
        off_front = abs((self.yaw - FRONT_ANGLE + 180) % 360 - 180)
        if off_back < 40 and abs(self.pitch) < 40:
            self.turn_to(BACK_ANGLE, steps=8)
        elif off_front < 25 and abs(self.pitch) < 25:
            self.turn_to(FRONT_ANGLE, steps=8)
        elif not self.showing_detailed:
            self.render(detailed=True)

    def _mouse_up(self, event):
        if self.drag_from is None:
            return
        self.drag_from = None
        if self.dragged:
            # The frame loop carries on: the keychain glides to a stop.
            self.dragging = False
            self.glide_speed = max(-MAX_GLIDE_SPEED,
                                   min(MAX_GLIDE_SPEED, self.glide_speed))
            return
        # A click (no drag): did it land on a button?
        label = self._button_at(event.x, event.y)
        if label:
            self.press(label)

    # ---- Mouse resting on a button -------------------------------------------

    def _button_at(self, x, y):
        """The button under this spot of the window, or None."""
        if not self.docked:
            return None
        r = keychain_model.BUTTON_RADIUS * SCALE
        for label, (bx, by) in keychain_model.BUTTON_SPOTS.items():
            if math.hypot(x - (CENTRE_X + bx * SCALE),
                          y - (CENTRE_Y - by * SCALE)) <= r:
                return label
        hx, hy = self._home_xy()
        if math.hypot(x - hx, y - hy) <= 14:
            return "HOME"
        return None

    def _mouse_hover(self, event):
        self._set_hover(self._button_at(event.x, event.y))

    def _set_hover(self, label):
        """Light up the button under the mouse and show a hand cursor."""
        if label == self.hover:
            return
        old = self.button_items.get(self.hover)
        if old and self.docked:
            self.canvas.itemconfig(old, fill=BUTTON_COLOR)
        self.hover = label
        new = self.button_items.get(label)
        if new and self.docked:
            self.canvas.itemconfig(new, fill=BUTTON_HOVER)
        self.canvas.configure(cursor="hand2" if label else "")

    # ---- Button presses ----------------------------------------------------

    def press(self, label):
        """Flash the button darker for a moment, then tell the app."""
        if self.animating:
            return
        if not self.docked:
            # The buttons are on the back: turn there first.
            self.turn_to(BACK_ANGLE)
            return
        item = self.button_items.get(label)
        if item:
            self.canvas.itemconfig(item, fill=BUTTON_PRESSED)

            def release():
                # The item may be gone if the keychain was turned meanwhile.
                if self.button_items.get(label) == item and self.docked:
                    self.canvas.itemconfig(
                        item, fill=BUTTON_HOVER if self.hover == label
                        else BUTTON_COLOR)
            self.canvas.after(150, release)
        self.on_button(label)
