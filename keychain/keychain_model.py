"""
keychain_model.py - builds the 3D shape of the keychain out of simple pieces.

The design follows the team's concept picture: a plush kidney character
with a face, little arms, a glucose meter in one hand, a stethoscope,
three coloured tubes on its side, a strap with a gold ring, and on the
back a cream frame holding the screen and three buttons.

Everything is made from four kinds of piece:
    ball   - a stretched ball (body, eyes, feet, buttons ...)
    tube   - a round pipe that follows a path (side tubes, stethoscope)
    block  - a box (glucose meter, strap)
    plate  - a flat shape with some thickness (the cream frame)

Directions: X = right, Y = up, Z = towards you when looking at the FACE.
The screen is on the back (the -Z side). One unit is about 110 pixels.

build_model(detail) returns a list of parts. Each part is a dict:
    name, colour, bias (a nudge so small parts are painted over the body),
    points [(x, y, z), ...] and faces [(point numbers ...), ...].
detail=1 is the light model used while turning, detail=2 the nicer one
used when the keychain is still.

Want to change a colour or move something? Look in build_model() below.
"""

import math

# ---- Main measurements -----------------------------------------------------
BODY_HALF_WIDTH = 1.6
BODY_HALF_HEIGHT = 1.95
BODY_HALF_DEPTH = 1.1
BODY_ROUNDNESS = 2.8     # 2 = egg shaped, bigger = more like a cushion

# The cream frame on the back: left, bottom, right, top.
FRAME_BOX = (-1.14, -1.12, 1.14, 1.50)
FRAME_CORNER = 0.42
FRAME_FACE_Z = -(BODY_HALF_DEPTH + 0.1)     # how far back its face is
SCREEN_CENTRE = (0.0, 0.41)
# Button centres on the back, as you see them from the back.
# LEFT and RIGHT are the arrow buttons, OK is the round one in the middle.
BUTTON_SPOTS = {"LEFT": (-0.56, -0.74), "OK": (0.0, -0.74), "RIGHT": (0.56, -0.74)}
BUTTON_RADIUS = 0.2
# The small Home button sits on the frame, above the screen.
HOME_SPOT = (0.0, 1.335)
HOME_RADIUS = 0.09

# ---- Colours ---------------------------------------------------------------
BODY = "#e9636c"
BODY_DARK = "#dc5560"
TUBE_RED, TUBE_BLUE, TUBE_YELLOW = "#d8383f", "#2f66c9", "#f2b632"
FRAME = "#f6d3b0"
BUTTON = "#f5a623"
GOLD = "#efb73a"
STRAP = "#ecc9a6"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _facing_out(points, faces, inside_point_for):
    """
    Make every face list its corners anticlockwise when seen from outside.
    inside_point_for(centre) must return a point that is inside the shape,
    near that face. The viewer relies on this to skip faces that point away.
    """
    fixed = []
    for face in faces:
        a, b, c = points[face[0]], points[face[len(face) // 3]], points[face[2 * len(face) // 3]]
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        n = len(face)
        mx = sum(points[i][0] for i in face) / n
        my = sum(points[i][1] for i in face) / n
        mz = sum(points[i][2] for i in face) / n
        ix, iy, iz = inside_point_for((mx, my, mz))
        if nx * (mx - ix) + ny * (my - iy) + nz * (mz - iz) < 0:
            face = tuple(reversed(face))
        fixed.append(tuple(face))
    return fixed


def ball(centre, radii, around, up, roundness=2.0, warp=None):
    """
    A stretched ball. centre and radii are (x, y, z). 'around' and 'up'
    say how many flat faces to use (more = smoother but slower).
    warp, if given, is a function that nudges each point (x, y, z).
    """
    power = 2.0 / roundness

    def bend(v):
        return math.copysign(abs(v) ** power, v)

    points, faces = [], []
    for j in range(up + 1):
        tilt = math.pi * (j / up - 0.5)              # -90 .. +90 degrees
        for i in range(around):
            turn = 2 * math.pi * i / around
            x = bend(math.cos(tilt) * math.cos(turn)) * radii[0]
            y = bend(math.sin(tilt)) * radii[1]
            z = bend(math.cos(tilt) * math.sin(turn)) * radii[2]
            if warp:
                x, y, z = warp(x, y, z)
            points.append((centre[0] + x, centre[1] + y, centre[2] + z))
    for j in range(up):
        for i in range(around):
            a = j * around + i
            b = j * around + (i + 1) % around
            c, d = b + around, a + around
            if j == 0:
                faces.append((a, c, d))              # bottom tip: triangles
            elif j == up - 1:
                faces.append((a, b, d))              # top tip: triangles
            else:
                faces.append((a, b, c, d))
    return points, _facing_out(points, faces, lambda m: centre)


def tube(path, radius, sides, closed=False):
    """A round pipe following the path, a list of (x, y, z) points."""
    points, faces = [], []
    count = len(path)
    for k, (px, py, pz) in enumerate(path):
        before = path[k - 1] if (k > 0 or closed) else path[k]
        after = path[(k + 1) % count] if (k < count - 1 or closed) else path[k]
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = math.hypot(dx, dy) or 1.0
        sx, sy = -dy / length, dx / length           # sideways, in the X-Y plane
        for s in range(sides):
            angle = 2 * math.pi * s / sides
            c, z = math.cos(angle) * radius, math.sin(angle) * radius
            points.append((px + sx * c, py + sy * c, pz + z))
    rings = count if closed else count - 1
    for k in range(rings):
        for s in range(sides):
            a = k * sides + s
            b = k * sides + (s + 1) % sides
            c = ((k + 1) % count) * sides + (s + 1) % sides
            d = ((k + 1) % count) * sides + s
            faces.append((a, b, c, d))
    if not closed:                                   # flat lids on both ends
        faces.append(tuple(range(sides)))
        faces.append(tuple(range((count - 1) * sides, count * sides)))

    def inside(m):
        return min(path, key=lambda p: (p[0] - m[0]) ** 2 + (p[1] - m[1]) ** 2
                   + (p[2] - m[2]) ** 2)
    # For the lids, "inside" is one step further along the path.
    fixed = _facing_out(points, faces[:rings * sides], inside)
    if not closed:
        fixed += _facing_out(points, faces[rings * sides:rings * sides + 1],
                             lambda m: path[1])
        fixed += _facing_out(points, faces[rings * sides + 1:],
                             lambda m: path[-2])
    return points, fixed


def block(centre, size, tilt_degrees=0.0):
    """A box. size is (width, height, depth). It can lean left or right."""
    cx, cy, cz = centre
    hw, hh, hd = size[0] / 2, size[1] / 2, size[2] / 2
    c, s = math.cos(math.radians(tilt_degrees)), math.sin(math.radians(tilt_degrees))
    points = []
    for z in (-hd, hd):
        for x, y in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
            points.append((cx + x * c - y * s, cy + x * s + y * c, cz + z))
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7)]
    return points, _facing_out(points, faces, lambda m: centre)


def rounded_outline(box, corner, steps):
    """Corner points (x, y) of a rounded rectangle. box = l, b, r, t."""
    left, bottom, right, top = box
    outline = []
    for cx, cy, start in ((right - corner, bottom + corner, -90),
                          (right - corner, top - corner, 0),
                          (left + corner, top - corner, 90),
                          (left + corner, bottom + corner, 180)):
        for i in range(steps + 1):
            a = math.radians(start + 90 * i / steps)
            outline.append((cx + corner * math.cos(a), cy + corner * math.sin(a)))
    return outline


def plate(outline, z_front, z_back):
    """A flat shape (list of (x, y)) with thickness, from z_front to z_back."""
    n = len(outline)
    points = [(x, y, z_front) for x, y in outline] + [(x, y, z_back) for x, y in outline]
    faces = [tuple(range(n)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mx = sum(x for x, _y in outline) / n
    my = sum(y for _x, y in outline) / n
    middle = (mx, my, (z_front + z_back) / 2)
    return points, _facing_out(points, faces, lambda m: middle)


def flat_shape(outline, z, facing_z):
    """A paper-thin shape at depth z that faces +Z (1) or -Z (-1)."""
    points = [(x, y, z) for x, y in outline]
    return points, _facing_out(points, [tuple(range(len(outline)))],
                               lambda m: (m[0], m[1], z - facing_z))


def circle_outline(cx, cy, radius, steps):
    return [(cx + radius * math.cos(2 * math.pi * i / steps),
             cy + radius * math.sin(2 * math.pi * i / steps)) for i in range(steps)]


def body_width_at(y):
    """The body is a little wider at the bottom than at the top (pear)."""
    return BODY_HALF_WIDTH * (1.0 - 0.10 * y / BODY_HALF_HEIGHT)


def body_surface_z(x, y):
    """How far forward the body's front surface is at (x, y)."""
    k = BODY_ROUNDNESS
    inside = 1 - abs(x / body_width_at(y)) ** k - abs(y / BODY_HALF_HEIGHT) ** k
    return BODY_HALF_DEPTH * max(inside, 0.0) ** (1 / k)


# ---------------------------------------------------------------------------
# The keychain
# ---------------------------------------------------------------------------

def build_model(detail=2):
    """Build every part. detail=1 light (fast), detail=2 nicer (slower)."""
    parts = []

    def add(name, colour, bias, shape):
        points, faces = shape
        parts.append({"name": name, "colour": colour, "bias": bias,
                      "points": points, "faces": faces})

    def on_front(x, y, lift=0.0):
        """A point sitting on the front of the body."""
        return (x, y, body_surface_z(x, y) + lift)

    small = (6, 4) if detail == 1 else (10, 6)       # faces for small balls
    medium = (8, 5) if detail == 1 else (14, 8)
    pipe_sides = 5 if detail == 1 else 8
    curve_steps = 5 if detail == 1 else 9

    # ---- Body: a plump cushion, with a dent on one side (kidney shape) ----
    def kidney(x, y, z):
        x *= 1.0 - 0.10 * y / BODY_HALF_HEIGHT       # pear: wider at the bottom
        if x > 0:                                    # dent where the tubes come out
            x -= 0.42 * (x / BODY_HALF_WIDTH) * math.exp(-((y - 0.25) / 0.6) ** 2)
        return x, y, z
    body_faces = (16, 10) if detail == 1 else (30, 18)
    add("body", BODY, 0.0,
        ball((0, 0, 0), (BODY_HALF_WIDTH, BODY_HALF_HEIGHT, BODY_HALF_DEPTH),
             *body_faces, roundness=BODY_ROUNDNESS, warp=kidney))

    # ---- Feet and arms ----
    for side in (-1, 1):
        add("foot", BODY_DARK, 0.0,
            ball((0.72 * side, -1.88, 0.2), (0.46, 0.26, 0.55), *medium))
    add("arm_right", BODY_DARK, 0.05,
        ball((1.02, -0.45, 0.86), (0.3, 0.26, 0.3), *medium))
    add("arm_left", BODY_DARK, 0.05,
        ball((-1.2, -0.3, 0.72), (0.32, 0.27, 0.32), *medium))

    # ---- Face ----
    for side in (-1, 1):
        ex, ey = 0.5 * side, 0.72
        add("eye", "#2a1a22", 0.12, ball(on_front(ex, ey, -0.02), (0.17, 0.21, 0.1), *small))
        add("eye_glint", "#ffffff", 0.22,
            ball(on_front(ex - 0.06, ey + 0.08, 0.08), (0.055, 0.06, 0.03), *small))
        add("blush", "#f7a3a8", 0.10, ball(on_front(0.9 * side, 0.4, -0.03), (0.22, 0.13, 0.06), *small))
    add("mouth", "#5c1f2e", 0.12, ball(on_front(0, 0.38, -0.02), (0.2, 0.17, 0.08), *small))
    add("tongue", "#f58a9b", 0.2, ball(on_front(0, 0.31, 0.03), (0.12, 0.08, 0.05), *small))

    # ---- Stethoscope: a blue U-shaped tube with a silver disc ----
    u_path = []
    for i in range(curve_steps * 2 + 1):
        a = math.pi * i / (curve_steps * 2)
        x, y = -0.72 * math.cos(a), 0.05 - 0.6 * math.sin(a)
        u_path.append(on_front(x, y, 0.04))
    add("stethoscope_tube", "#2f6fd0", 0.16, tube(u_path, 0.065, pipe_sides))
    add("stethoscope_drop", "#2f6fd0", 0.16,
        tube([on_front(0, -0.55, 0.04), on_front(0, -0.8, 0.06)], 0.06, pipe_sides))
    add("stethoscope_disc", "#c9ced6", 0.2, ball(on_front(0, -0.95, 0.06), (0.2, 0.2, 0.08), *medium))
    add("stethoscope_centre", "#8f99a5", 0.28, ball(on_front(0, -0.95, 0.12), (0.11, 0.11, 0.04), *small))

    # ---- Glucose meter held in the left hand ----
    mx, my, mz = -1.02, -0.2, 0.98
    add("meter", "#f4f6f9", 0.2, block((mx, my, mz), (0.52, 0.78, 0.14), tilt_degrees=14))
    add("meter_screen", "#bcd9f2", 0.3, block((mx - 0.03, my + 0.1, mz + 0.08), (0.36, 0.4, 0.03), tilt_degrees=14))
    add("meter_drop", "#d8383f", 0.4, ball((mx - 0.03, my + 0.08, mz + 0.11), (0.08, 0.11, 0.03), *small))
    add("meter_strip", "#dfe4ea", 0.2, block((mx + 0.09, my - 0.47, mz), (0.16, 0.2, 0.06), tilt_degrees=14))

    # ---- Three plush tubes on the side ----
    def bend_path(points_2d):
        """Smooth a few (x, y) points into a curved path at z = 0."""
        path = []
        n = len(points_2d) - 1
        for i in range(n * curve_steps // 2 + 1):
            t = i / (n * curve_steps // 2) * n
            k = min(int(t), n - 1)
            f = t - k
            f = f * f * (3 - 2 * f)
            (x0, y0), (x1, y1) = points_2d[k], points_2d[k + 1]
            path.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, 0.0))
        return path
    add("tube_red", TUBE_RED, 0.0,
        tube(bend_path([(1.0, 0.55), (1.55, 0.7), (1.85, 1.0), (1.8, 1.35)]), 0.17, pipe_sides))
    add("tube_blue", TUBE_BLUE, 0.0,
        tube(bend_path([(1.0, 0.25), (1.5, 0.3), (1.95, 0.42)]), 0.17, pipe_sides))
    add("tube_yellow", TUBE_YELLOW, 0.0,
        tube(bend_path([(1.0, -0.05), (1.6, -0.1), (1.9, -0.5), (1.75, -1.0), (1.3, -1.2)]),
             0.17, pipe_sides))

    # ---- Strap and gold ring on top ----
    add("strap", STRAP, 0.0, block((0, BODY_HALF_HEIGHT + 0.14, 0), (0.3, 0.42, 0.12)))
    ring_steps = 10 if detail == 1 else 20
    ring_path = [(0.33 * math.cos(2 * math.pi * i / ring_steps),
                  BODY_HALF_HEIGHT + 0.6 + 0.33 * math.sin(2 * math.pi * i / ring_steps), 0.0)
                 for i in range(ring_steps)]
    add("ring", GOLD, 0.0, tube(ring_path, 0.075, pipe_sides, closed=True))

    # ---- Back: cream frame, screen glass, buttons, speaker, charging port ----
    corner_steps = 3 if detail == 1 else 6
    frame_outline = rounded_outline(FRAME_BOX, FRAME_CORNER, corner_steps)
    add("frame", FRAME, 0.05, plate(frame_outline, FRAME_FACE_Z, FRAME_FACE_Z + 0.34))
    # Its flat face again, with a big nudge so the body never paints over it.
    add("frame_face", FRAME, 0.5, flat_shape(frame_outline, FRAME_FACE_Z - 0.004, -1))
    # The glass (shown while turning; the live screen replaces it when still).
    sx, sy = SCREEN_CENTRE
    for grow, colour, bias in ((0.0, "#e7b592", 0.8), (-0.035, "#c9e4a6", 0.9)):
        glass = (-sx - 0.965 - grow, sy - 0.78 - grow, -sx + 0.965 + grow, sy + 0.78 + grow)
        add("glass", colour, bias,
            flat_shape(rounded_outline(glass, 0.26 + grow, corner_steps), FRAME_FACE_Z - 0.01, -1))
    for label, (bx, by) in BUTTON_SPOTS.items():
        # x is flipped because these spots are "as seen from the back"
        add("button_" + label.lower(), BUTTON, 1.0,
            ball((-bx, by, FRAME_FACE_Z), (BUTTON_RADIUS, BUTTON_RADIUS, 0.09), *medium))
    hx, hy = HOME_SPOT
    add("button_home", BUTTON, 1.0,
        ball((-hx, hy, FRAME_FACE_Z), (HOME_RADIUS, HOME_RADIUS, 0.05), *medium))
    for row in range(2):
        for col in (-1, 0, 1):
            hx, hy = 0.16 * col, -1.34 - 0.13 * row
            hz = -body_surface_z(hx, hy) - 0.02
            add("speaker_hole", "#8f3340", 0.15,
                flat_shape(circle_outline(hx, hy, 0.04, 6), hz, -1))
    # Charging port underneath
    port = rounded_outline((-0.2, -0.07, 0.2, 0.07), 0.06, 2)
    port_points = [(x, -BODY_HALF_HEIGHT - 0.01, z) for x, z in port]
    add("charging_port", "#4a2a33", 0.2,
        (port_points, _facing_out(port_points, [tuple(range(len(port_points)))],
                                  lambda m: (0, 0, 0))))
    return parts
