import pygame
import math
import json
import tkinter as tk
from tkinter import filedialog

pygame.init()

WIDTH, HEIGHT = 1500, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drawing Tool")

# ============================================================
# COLORS
# ============================================================

COLORS = {
    pygame.K_1: ("Red", (255, 80, 80)),
    pygame.K_2: ("Green", (80, 220, 120)),
    pygame.K_3: ("Blue", (80, 160, 255)),
    pygame.K_4: ("Yellow", (255, 220, 70)),
    pygame.K_5: ("Purple", (190, 100, 255)),
    pygame.K_6: ("White", (255, 255, 255)),
}

BACKGROUND = (30, 30, 30)
TEXT_COLOR = (200, 200, 200)
PREVIEW_COLOR = (150, 150, 150)
SNAP_COLOR = (255, 180, 0)

SNAP_DISTANCE = 15

# Distance from a shape at which the eraser deletes it.
DELETE_DISTANCE = 8

# ============================================================
# CAMERA
# ============================================================

zoom = 1.0
camera_offset = [0.0, 0.0]

MIN_ZOOM = 0.1
MAX_ZOOM = 10.0

# ============================================================
# DRAWING DATA
# ============================================================

circles = []
lines = []
beziers = []
points_data = []

tool = "circle"
points = []

current_color = (255, 80, 80)
current_color_name = "Red"

font = pygame.font.Font(None, 28)

running = True

# ============================================================
# COORDINATE CONVERSION
# ============================================================

def world_to_screen(pos):

    return (
        int(pos[0] * zoom + camera_offset[0]),
        int(pos[1] * zoom + camera_offset[1])
    )


def screen_to_world(pos):

    return (
        (pos[0] - camera_offset[0]) / zoom,
        (pos[1] - camera_offset[1]) / zoom
    )


def screen_radius(radius):

    return max(1, int(radius * zoom))


# ============================================================
# BEZIER
# ============================================================

def quadratic_bezier(p0, p1, p2, t):

    x = (
        (1 - t) ** 2 * p0[0]
        + 2 * (1 - t) * t * p1[0]
        + t ** 2 * p2[0]
    )

    y = (
        (1 - t) ** 2 * p0[1]
        + 2 * (1 - t) * t * p1[1]
        + t ** 2 * p2[1]
    )

    return x, y


def draw_bezier(surface, p0, p1, p2, color, width=2):

    curve_points = []

    for i in range(101):

        t = i / 100

        point = quadratic_bezier(
            p0,
            p1,
            p2,
            t
        )

        curve_points.append(
            world_to_screen(point)
        )

    pygame.draw.lines(
        surface,
        color,
        False,
        curve_points,
        max(1, int(width))
    )


# ============================================================
# SNAP POINTS
# ============================================================

def get_snap_points():

    snap_points = []

    # Lines
    for start, end, color in lines:

        snap_points.append(start)
        snap_points.append(end)

    # Beziers
    for p0, p1, p2, color in beziers:

        snap_points.append(p0)
        snap_points.append(p2)

    # Circles
    for center, radius, color in circles:

        cx, cy = center
        r = radius

        snap_points.append(center)

        snap_points.append(
            (cx, cy - r)
        )

        snap_points.append(
            (cx + r, cy)
        )

        snap_points.append(
            (cx, cy + r)
        )

        snap_points.append(
            (cx - r, cy)
        )

    # Points
    for position, color in points_data:

        snap_points.append(position)

    # Intersections
    snap_points.extend(
        get_intersection_snap_points()
    )

    return snap_points


def get_snap_position(mouse_screen_pos):

    closest_point = None
    closest_distance = SNAP_DISTANCE

    for world_point in get_snap_points():

        screen_point = world_to_screen(world_point)

        distance = math.hypot(
            mouse_screen_pos[0] - screen_point[0],
            mouse_screen_pos[1] - screen_point[1]
        )

        if distance <= closest_distance:

            closest_distance = distance
            closest_point = world_point

    return closest_point


# ============================================================
# INTERSECTIONS
# ============================================================

def line_segment_intersection(p1, p2, p3, p4):

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denominator = (
        (x1 - x2) * (y3 - y4)
        - (y1 - y2) * (x3 - x4)
    )

    if abs(denominator) < 1e-10:
        return None

    t = (
        (x1 - x3) * (y3 - y4)
        - (y1 - y3) * (x3 - x4)
    ) / denominator

    u = -(
        (x1 - x2) * (y1 - y3)
        - (y1 - y2) * (x1 - x3)
    ) / denominator

    if 0 <= t <= 1 and 0 <= u <= 1:

        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        return (x, y)

    return None


def shape_to_segments(shape):

    shape_type, data = shape

    segments = []

    # Line
    if shape_type == "line":

        start, end = data

        segments.append(
            (start, end)
        )

    # Bezier
    elif shape_type == "bezier":

        p0, p1, p2 = data

        steps = 100

        previous = quadratic_bezier(
            p0,
            p1,
            p2,
            0
        )

        for i in range(1, steps + 1):

            t = i / steps

            current = quadratic_bezier(
                p0,
                p1,
                p2,
                t
            )

            segments.append(
                (previous, current)
            )

            previous = current

    # Circle
    elif shape_type == "circle":

        center, radius = data

        steps = 128

        previous = (
            center[0] + radius,
            center[1]
        )

        for i in range(1, steps + 1):

            angle = (
                2 * math.pi * i / steps
            )

            current = (
                center[0]
                + radius * math.cos(angle),

                center[1]
                + radius * math.sin(angle)
            )

            segments.append(
                (previous, current)
            )

            previous = current

    return segments


def get_intersection_snap_points():

    shapes = []

    # Lines
    for start, end, color in lines:

        shapes.append(
            (
                "line",
                (start, end)
            )
        )

    # Beziers
    for p0, p1, p2, color in beziers:

        shapes.append(
            (
                "bezier",
                (p0, p1, p2)
            )
        )

    # Circles
    for center, radius, color in circles:

        shapes.append(
            (
                "circle",
                (center, radius)
            )
        )

    intersection_points = []

    for i in range(len(shapes)):

        segments_a = shape_to_segments(
            shapes[i]
        )

        for j in range(i + 1, len(shapes)):

            segments_b = shape_to_segments(
                shapes[j]
            )

            for a1, a2 in segments_a:

                for b1, b2 in segments_b:

                    intersection = line_segment_intersection(
                        a1,
                        a2,
                        b1,
                        b2
                    )

                    if intersection is not None:

                        intersection_points.append(
                            intersection
                        )

    return intersection_points


# ============================================================
# DISTANCE HELPERS
# ============================================================

def distance_to_segment(point, a, b):

    px, py = point
    ax, ay = a
    bx, by = b

    dx = bx - ax
    dy = by - ay

    length_squared = dx * dx + dy * dy

    if length_squared == 0:

        return math.hypot(
            px - ax,
            py - ay
        )

    t = (
        (px - ax) * dx
        + (py - ay) * dy
    ) / length_squared

    t = max(0, min(1, t))

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.hypot(
        px - closest_x,
        py - closest_y
    )


def distance_to_bezier(point, p0, p1, p2):

    closest = float("inf")

    previous = quadratic_bezier(
        p0,
        p1,
        p2,
        0
    )

    for i in range(1, 101):

        t = i / 100

        current = quadratic_bezier(
            p0,
            p1,
            p2,
            t
        )

        distance = distance_to_segment(
            point,
            previous,
            current
        )

        closest = min(
            closest,
            distance
        )

        previous = current

    return closest


# ============================================================
# DELETE SHAPE UNDER MOUSE
# ============================================================

def delete_at_position(mouse_screen_pos):

    mouse_world = screen_to_world(
        mouse_screen_pos
    )

    # Convert screen tolerance to world tolerance.
    tolerance = DELETE_DISTANCE / zoom

    # --------------------------------------------------------
    # Points
    # --------------------------------------------------------

    for i in range(len(points_data) - 1, -1, -1):

        position, color = points_data[i]

        distance = math.hypot(
            mouse_world[0] - position[0],
            mouse_world[1] - position[1]
        )

        if distance <= tolerance:

            points_data.pop(i)
            return True

    # --------------------------------------------------------
    # Lines
    # --------------------------------------------------------

    for i in range(len(lines) - 1, -1, -1):

        start, end, color = lines[i]

        distance = distance_to_segment(
            mouse_world,
            start,
            end
        )

        if distance <= tolerance:

            lines.pop(i)
            return True

    # --------------------------------------------------------
    # Beziers
    # --------------------------------------------------------

    for i in range(len(beziers) - 1, -1, -1):

        p0, p1, p2, color = beziers[i]

        distance = distance_to_bezier(
            mouse_world,
            p0,
            p1,
            p2
        )

        if distance <= tolerance:

            beziers.pop(i)
            return True

    # --------------------------------------------------------
    # Circles
    # --------------------------------------------------------

    for i in range(len(circles) - 1, -1, -1):

        center, radius, color = circles[i]

        distance_from_center = math.hypot(
            mouse_world[0] - center[0],
            mouse_world[1] - center[1]
        )

        distance_from_edge = abs(
            distance_from_center - radius
        )

        if distance_from_edge <= tolerance:

            circles.pop(i)
            return True

    return False


# ============================================================
# FILE HANDLING
# ============================================================

def save_drawing():

    root = tk.Tk()
    root.withdraw()

    filename = filedialog.asksaveasfilename(
        title="Save Drawing",
        defaultextension=".draw",
        filetypes=[
            ("Drawing files", "*.draw"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if not filename:
        return

    data = {
        "version": 3,

        "view": {
            "zoom": zoom,
            "camera_offset": camera_offset
        },

        "points": [
            {
                "position": list(position),
                "color": list(color)
            }
            for position, color in points_data
        ],

        "circles": [
            {
                "center": list(center),
                "radius": radius,
                "color": list(color)
            }
            for center, radius, color in circles
        ],

        "lines": [
            {
                "start": list(start),
                "end": list(end),
                "color": list(color)
            }
            for start, end, color in lines
        ],

        "beziers": [
            {
                "p0": list(p0),
                "p1": list(p1),
                "p2": list(p2),
                "color": list(color)
            }
            for p0, p1, p2, color in beziers
        ]
    }

    try:

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Drawing saved to: {filename}")

    except Exception as e:

        print(f"Error saving drawing: {e}")


def load_drawing():

    global circles
    global lines
    global beziers
    global points_data
    global points
    global zoom
    global camera_offset

    root = tk.Tk()
    root.withdraw()

    filename = filedialog.askopenfilename(
        title="Load Drawing",
        filetypes=[
            ("Drawing files", "*.draw"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if not filename:
        return

    try:

        with open(filename, "r") as file:
            data = json.load(file)

        # Points
        new_points = []

        for point in data.get("points", []):

            position = tuple(
                point["position"]
            )

            color = tuple(
                point["color"]
            )

            new_points.append(
                (position, color)
            )

        # Circles
        new_circles = []

        for circle in data.get("circles", []):

            center = tuple(
                circle["center"]
            )

            radius = float(
                circle["radius"]
            )

            color = tuple(
                circle["color"]
            )

            new_circles.append(
                (
                    center,
                    radius,
                    color
                )
            )

        # Lines
        new_lines = []

        for line in data.get("lines", []):

            start = tuple(
                line["start"]
            )

            end = tuple(
                line["end"]
            )

            color = tuple(
                line["color"]
            )

            new_lines.append(
                (
                    start,
                    end,
                    color
                )
            )

        # Beziers
        new_beziers = []

        for bezier in data.get("beziers", []):

            p0 = tuple(bezier["p0"])
            p1 = tuple(bezier["p1"])
            p2 = tuple(bezier["p2"])

            color = tuple(
                bezier["color"]
            )

            new_beziers.append(
                (
                    p0,
                    p1,
                    p2,
                    color
                )
            )

        # View
        view = data.get(
            "view",
            {}
        )

        loaded_zoom = float(
            view.get(
                "zoom",
                1.0
            )
        )

        loaded_offset = view.get(
            "camera_offset",
            [0.0, 0.0]
        )

        loaded_zoom = max(
            MIN_ZOOM,
            min(MAX_ZOOM, loaded_zoom)
        )

        # Apply
        points_data = new_points
        circles = new_circles
        lines = new_lines
        beziers = new_beziers

        zoom = loaded_zoom

        camera_offset = [
            float(loaded_offset[0]),
            float(loaded_offset[1])
        ]

        points = []

        print(f"Drawing loaded from: {filename}")

    except Exception as e:

        print(f"Error loading drawing: {e}")


def new_drawing():

    global circles
    global lines
    global beziers
    global points_data
    global points

    circles = []
    lines = []
    beziers = []
    points_data = []
    points = []

    reset_view()


# ============================================================
# CAMERA
# ============================================================

def reset_view():

    global zoom
    global camera_offset

    zoom = 1.0

    camera_offset = [
        0.0,
        0.0
    ]


def zoom_at_mouse(mouse_pos, zoom_factor):

    global zoom
    global camera_offset

    world_before = screen_to_world(
        mouse_pos
    )

    new_zoom = zoom * zoom_factor

    new_zoom = max(
        MIN_ZOOM,
        min(MAX_ZOOM, new_zoom)
    )

    zoom = new_zoom

    camera_offset[0] = (
        mouse_pos[0]
        - world_before[0] * zoom
    )

    camera_offset[1] = (
        mouse_pos[1]
        - world_before[1] * zoom
    )


# ============================================================
# MAIN LOOP
# ============================================================

panning = False
pan_start_mouse = None
pan_start_offset = None

deleting = False

while running:

    mouse_pos = pygame.mouse.get_pos()

    snap_pos = get_snap_position(
        mouse_pos
    )

    if snap_pos is not None:

        draw_pos = world_to_screen(
            snap_pos
        )

    else:

        draw_pos = mouse_pos

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ====================================================
        # KEYBOARD
        # ====================================================

        elif event.type == pygame.KEYDOWN:

            # Tools
            if event.key == pygame.K_c:

                tool = "circle"
                points = []

            elif event.key == pygame.K_l:

                tool = "line"
                points = []

            elif event.key == pygame.K_b:

                tool = "bezier"
                points = []

            elif event.key == pygame.K_p:

                tool = "point"
                points = []

            elif event.key == pygame.K_d:

                tool = "delete"
                points = []

            # Cancel
            elif event.key == pygame.K_ESCAPE:

                points = []

            # Reset view
            elif event.key == pygame.K_HOME:

                reset_view()

            # Colors
            elif event.key in COLORS:

                current_color_name, current_color = COLORS[
                    event.key
                ]

            # Save
            elif (
                event.key == pygame.K_s
                and pygame.key.get_mods() & pygame.KMOD_CTRL
            ):

                save_drawing()

            # Load
            elif (
                event.key == pygame.K_o
                and pygame.key.get_mods() & pygame.KMOD_CTRL
            ):

                load_drawing()

            # New
            elif (
                event.key == pygame.K_n
                and pygame.key.get_mods() & pygame.KMOD_CTRL
            ):

                new_drawing()

        # ====================================================
        # MOUSE WHEEL
        # ====================================================

        elif event.type == pygame.MOUSEWHEEL:

            if event.y > 0:

                zoom_at_mouse(
                    pygame.mouse.get_pos(),
                    1.15
                )

            elif event.y < 0:

                zoom_at_mouse(
                    pygame.mouse.get_pos(),
                    1 / 1.15
                )

        # ====================================================
        # MOUSE BUTTON DOWN
        # ====================================================

        elif event.type == pygame.MOUSEBUTTONDOWN:

            # ------------------------------------------------
            # LEFT CLICK
            # ------------------------------------------------

            if event.button == 1:

                # Delete tool
                if tool == "delete":

                    deleting = True

                    delete_at_position(
                        event.pos
                    )

                # Normal drawing
                else:

                    snapped = get_snap_position(
                        event.pos
                    )

                    if snapped is not None:

                        click_pos = snapped

                    else:

                        click_pos = screen_to_world(
                            event.pos
                        )

                    # Point tool
                    if tool == "point":

                        points_data.append(
                            (
                                click_pos,
                                current_color
                            )
                        )

                        points = []

                    # Other tools
                    else:

                        points.append(
                            click_pos
                        )

                        # Circle
                        if tool == "circle":

                            if len(points) == 2:

                                center = points[0]

                                dx = (
                                    points[1][0]
                                    - center[0]
                                )

                                dy = (
                                    points[1][1]
                                    - center[1]
                                )

                                radius = math.hypot(
                                    dx,
                                    dy
                                )

                                circles.append(
                                    (
                                        center,
                                        radius,
                                        current_color
                                    )
                                )

                                points = []

                        # Line
                        elif tool == "line":

                            if len(points) == 2:

                                lines.append(
                                    (
                                        points[0],
                                        points[1],
                                        current_color
                                    )
                                )

                                points = []

                        # Bezier
                        elif tool == "bezier":

                            if len(points) == 3:

                                beziers.append(
                                    (
                                        points[0],
                                        points[1],
                                        points[2],
                                        current_color
                                    )
                                )

                                points = []

            # ------------------------------------------------
            # MIDDLE CLICK = PAN
            # ------------------------------------------------

            elif event.button == 2:

                panning = True

                pan_start_mouse = event.pos

                pan_start_offset = (
                    camera_offset.copy()
                )

        # ====================================================
        # MOUSE BUTTON UP
        # ====================================================

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                deleting = False

            elif event.button == 2:

                panning = False

        # ====================================================
        # MOUSE MOTION
        # ====================================================

        elif event.type == pygame.MOUSEMOTION:

            # Pan
            if panning:

                dx = (
                    event.pos[0]
                    - pan_start_mouse[0]
                )

                dy = (
                    event.pos[1]
                    - pan_start_mouse[1]
                )

                camera_offset[0] = (
                    pan_start_offset[0]
                    + dx
                )

                camera_offset[1] = (
                    pan_start_offset[1]
                    + dy
                )

            # Delete while dragging
            if deleting and tool == "delete":

                delete_at_position(
                    event.pos
                )

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    screen.fill(BACKGROUND)

    # ========================================================
    # DRAW CIRCLES
    # ========================================================

    for center, radius, color in circles:

        pygame.draw.circle(
            screen,
            color,
            world_to_screen(center),
            screen_radius(radius),
            max(1, int(2 * zoom))
        )

    # ========================================================
    # DRAW LINES
    # ========================================================

    for start, end, color in lines:

        pygame.draw.line(
            screen,
            color,
            world_to_screen(start),
            world_to_screen(end),
            max(1, int(2 * zoom))
        )

    # ========================================================
    # DRAW BEZIERS
    # ========================================================

    for p0, p1, p2, color in beziers:

        draw_bezier(
            screen,
            p0,
            p1,
            p2,
            color,
            max(1, int(2 * zoom))
        )

    # ========================================================
    # DRAW POINTS
    # ========================================================

    for position, color in points_data:

        pygame.draw.circle(
            screen,
            color,
            world_to_screen(position),
            5
        )

    # ========================================================
    # PREVIEW
    # ========================================================

    if tool == "circle" and len(points) == 1:

        center = world_to_screen(
            points[0]
        )

        dx = draw_pos[0] - center[0]
        dy = draw_pos[1] - center[1]

        radius = math.hypot(
            dx,
            dy
        )

        pygame.draw.circle(
            screen,
            current_color,
            center,
            int(radius),
            1
        )

        pygame.draw.circle(
            screen,
            current_color,
            center,
            4
        )

    elif tool == "line" and len(points) == 1:

        pygame.draw.line(
            screen,
            current_color,
            world_to_screen(points[0]),
            draw_pos,
            1
        )

        pygame.draw.circle(
            screen,
            current_color,
            world_to_screen(points[0]),
            4
        )

    elif tool == "bezier":

        if len(points) == 1:

            pygame.draw.line(
                screen,
                PREVIEW_COLOR,
                world_to_screen(points[0]),
                draw_pos,
                1
            )

            pygame.draw.circle(
                screen,
                current_color,
                world_to_screen(points[0]),
                4
            )

        elif len(points) == 2:

            p0 = points[0]
            p1 = points[1]
            p2 = screen_to_world(draw_pos)

            pygame.draw.line(
                screen,
                PREVIEW_COLOR,
                world_to_screen(p0),
                world_to_screen(p1),
                1
            )

            pygame.draw.line(
                screen,
                PREVIEW_COLOR,
                world_to_screen(p1),
                draw_pos,
                1
            )

            draw_bezier(
                screen,
                p0,
                p1,
                p2,
                current_color,
                1
            )

            pygame.draw.circle(
                screen,
                current_color,
                world_to_screen(p0),
                4
            )

            pygame.draw.circle(
                screen,
                current_color,
                world_to_screen(p1),
                4
            )

    # ========================================================
    # SNAP INDICATOR
    # ========================================================

    if snap_pos is not None and tool != "delete":

        pygame.draw.circle(
            screen,
            SNAP_COLOR,
            world_to_screen(snap_pos),
            7,
            2
        )

        pygame.draw.circle(
            screen,
            SNAP_COLOR,
            world_to_screen(snap_pos),
            3
        )

    # ========================================================
    # DELETE CURSOR
    # ========================================================

    if tool == "delete":

        pygame.draw.circle(
            screen,
            (255, 80, 80),
            mouse_pos,
            DELETE_DISTANCE,
            2
        )

    # ========================================================
    # UI
    # ========================================================

    tool_text = font.render(
        f"Tool: {tool.upper()}   |   "
        f"C = Circle   L = Line   B = Bezier   "
        f"P = Point   D = Delete   |   ESC = Cancel",
        True,
        TEXT_COLOR
    )

    screen.blit(
        tool_text,
        (15, 15)
    )

    color_text = font.render(
        f"Color: {current_color_name}   |   "
        f"1-6 = Change Color",
        True,
        current_color
    )

    screen.blit(
        color_text,
        (15, 45)
    )

    snap_text = font.render(
        f"Snap: {SNAP_DISTANCE}px",
        True,
        SNAP_COLOR
    )

    screen.blit(
        snap_text,
        (15, 110)
    )

    file_text = font.render(
        "CTRL+S = Save   CTRL+O = Load   CTRL+N = New",
        True,
        TEXT_COLOR
    )

    screen.blit(
        file_text,
        (15, 140)
    )

    view_text = font.render(
        f"Zoom: {zoom:.2f}x   |   "
        f"Wheel = Zoom   Middle Mouse = Pan   Home = Reset",
        True,
        TEXT_COLOR
    )

    screen.blit(
        view_text,
        (15, 170)
    )

    if tool == "delete":

        delete_text = font.render(
            "DELETE: Hold LEFT CLICK and drag over shapes",
            True,
            (255, 100, 100)
        )

        screen.blit(
            delete_text,
            (15, 200)
        )

    # ========================================================
    # COLOR PALETTE
    # ========================================================

    x = 15
    y = 80

    for key, (name, color) in COLORS.items():

        pygame.draw.rect(
            screen,
            color,
            (x, y, 30, 30)
        )

        if color == current_color:

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (x - 2, y - 2, 34, 34),
                2
            )

        number = pygame.key.name(key)

        number_text = font.render(
            number,
            True,
            TEXT_COLOR
        )

        screen.blit(
            number_text,
            (x + 40, y + 3)
        )

        x += 75

    pygame.display.flip()


pygame.quit()
