
import math
import random
import textwrap

import pygame

from data import (
    World,
    Planet,
    Spacecraft,
    Building,
    RESOURCE_TYPES,
    RESOURCE_KEYS,
    RAW_RESOURCE_KEYS,
    RESOURCE_TRANSFER_AMOUNT,
    create_default_world,
    BUILDING_WIDTH,
    BUILDING_HEIGHT,
    BUILDING_GAP,
    ROCKET_LENGTH,
    ROCKET_WIDTH,
    HALF_LENGTH,
    HALF_WIDTH,
    ROCKET_MASS,
    ROCKET_INERTIA,
    ROCKET_THRUST_FORCE,
    ROTATION_ACCELERATION,
    ANGULAR_DAMPING,
    RESTITUTION,
    FRICTION,
    MAX_PHYSICS_STEP,
)


# ============================================================
# CONFIGURATION
# ============================================================

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

BACKGROUND_COLOR = (8, 10, 22)

CAMERA_SPEED = 500.0
ZOOM_SPEED = 1.15
MIN_ZOOM = 0.1
MAX_ZOOM = 5.0

INV_MASS = 1.0 / ROCKET_MASS
INV_INERTIA = 1.0 / ROCKET_INERTIA

TAU = math.tau

# Trajectory prediction
TRAJECTORY_DURATION = 20.0
TRAJECTORY_STEP = 0.05
TRAJECTORY_COLOR = (90, 230, 170)

screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    pygame.RESIZABLE,
)

pygame.display.set_caption(
    "Interplanetary Colony Simulator"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 15)
small_font = pygame.font.SysFont("consolas", 12)
panel_font = pygame.font.SysFont("consolas", 14)

show_controls = True

# Initial selected resource
selected_resource = "raw_blue"

# Button rectangles are refreshed during rendering.
resource_button_rects = {}
load_button_rect = pygame.Rect(0, 0, 0, 0)
unload_button_rect = pygame.Rect(0, 0, 0, 0)


# ============================================================
# CAMERA
# ============================================================

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.zoom = 0.75

        self.dragging = False
        self.last_mouse_pos = (0, 0)

    def world_to_screen(self, x, y):
        cx = screen.get_width() / 2
        cy = screen.get_height() / 2

        sx = (x - self.x) * self.zoom + cx
        sy = (y - self.y) * self.zoom + cy

        return round(sx), round(sy)

    def screen_to_world(self, x, y):
        cx = screen.get_width() / 2
        cy = screen.get_height() / 2

        wx = (x - cx) / self.zoom + self.x
        wy = (y - cy) / self.zoom + self.y

        return wx, wy

    def move(self, dx, dy, dt):
        self.x += dx * CAMERA_SPEED * dt / self.zoom
        self.y += dy * CAMERA_SPEED * dt / self.zoom

    def zoom_at(self, mouse_x, mouse_y, factor):
        before_x, before_y = self.screen_to_world(
            mouse_x, mouse_y
        )

        self.zoom = max(
            MIN_ZOOM,
            min(MAX_ZOOM, self.zoom * factor),
        )

        after_x, after_y = self.screen_to_world(
            mouse_x, mouse_y
        )

        self.x += before_x - after_x
        self.y += before_y - after_y


camera = Camera()


# ============================================================
# RESOURCE ICONS
# ============================================================

def draw_resource_icon(
    target,
    resource_key,
    center,
    size,
    background_color,
):
    """
    Draw the requested icon for a resource type.

    Raw:
        Blue square, red circle, green triangle.

    Refined:
        Blue octagon, red pentagon, green torus.

    Advanced:
        White star.
    """

    info = RESOURCE_TYPES[resource_key]

    color = info.color
    cx, cy = center
    radius = max(2, size / 2.0)

    if info.shape == "square":
        rect = pygame.Rect(
            round(cx - radius),
            round(cy - radius),
            round(radius * 2),
            round(radius * 2),
        )
        pygame.draw.rect(target, color, rect)

    elif info.shape == "circle":
        pygame.draw.circle(
            target,
            color,
            (round(cx), round(cy)),
            round(radius),
        )

    elif info.shape in ("triangle", "pentagon", "octagon", "star"):
        if info.shape == "triangle":
            point_count = 3
        elif info.shape == "pentagon":
            point_count = 5
        elif info.shape == "octagon":
            point_count = 8
        else:
            point_count = 10

        points = []

        for i in range(point_count):
            angle = -math.pi / 2 + (
                i * TAU / point_count
            )

            if info.shape == "star" and i % 2 == 1:
                point_radius = radius * 0.43
            else:
                point_radius = radius

            points.append((
                round(cx + math.cos(angle) * point_radius),
                round(cy + math.sin(angle) * point_radius),
            ))

        pygame.draw.polygon(target, color, points)

    elif info.shape == "torus":
        pygame.draw.circle(
            target,
            color,
            (round(cx), round(cy)),
            round(radius),
        )

        # Make the central hole transparent-looking by drawing
        # the button or planet background color over it.
        pygame.draw.circle(
            target,
            background_color,
            (round(cx), round(cy)),
            max(1, round(radius * 0.42)),
        )


# ============================================================
# SPACECRAFT COORDINATE TRANSFORMS
# ============================================================

def local_to_world(ship, lx, ly):
    c = math.cos(ship.angle)
    s = math.sin(ship.angle)

    return (
        ship.x + lx * c - ly * s,
        ship.y + lx * s + ly * c,
    )


# ============================================================
# PHYSICS: RECTANGLE VS. CIRCLE COLLISION
# ============================================================

def find_collision(ship, planet):
    """
    Test a rotated rectangle against a circular planet.

    Return:
        normal_x, normal_y, penetration, contact_x, contact_y

    Or None if no collision exists.
    """

    c = math.cos(ship.angle)
    s = math.sin(ship.angle)

    dx = planet.x - ship.x
    dy = planet.y - ship.y

    # Planet center in rocket-local coordinates.
    local_x = dx * c + dy * s
    local_y = -dx * s + dy * c

    # Closest point on the rocket rectangle.
    closest_x = max(
        -HALF_LENGTH,
        min(HALF_LENGTH, local_x),
    )

    closest_y = max(
        -HALF_WIDTH,
        min(HALF_WIDTH, local_y),
    )

    # Vector from the planet center towards the rectangle.
    diff_local_x = closest_x - local_x
    diff_local_y = closest_y - local_y

    diff_x = diff_local_x * c - diff_local_y * s
    diff_y = diff_local_x * s + diff_local_y * c

    distance = math.hypot(diff_x, diff_y)

    if distance >= planet.radius:
        return None

    if distance > 1e-8:
        nx = diff_x / distance
        ny = diff_y / distance
        penetration = planet.radius - distance

    else:
        # Deep-overlap fallback: select the nearest exit face.
        options = [
            (
                planet.radius + HALF_LENGTH + local_x,
                c, s,
                -HALF_LENGTH,
                max(-HALF_WIDTH, min(HALF_WIDTH, local_y)),
            ),
            (
                planet.radius + HALF_LENGTH - local_x,
                -c, -s,
                HALF_LENGTH,
                max(-HALF_WIDTH, min(HALF_WIDTH, local_y)),
            ),
            (
                planet.radius + HALF_WIDTH + local_y,
                -s, c,
                max(-HALF_LENGTH, min(HALF_LENGTH, local_x)),
                -HALF_WIDTH,
            ),
            (
                planet.radius + HALF_WIDTH - local_y,
                s, -c,
                max(-HALF_LENGTH, min(HALF_LENGTH, local_x)),
                HALF_WIDTH,
            ),
        ]

        (
            penetration,
            nx,
            ny,
            closest_x,
            closest_y,
        ) = min(options, key=lambda option: option[0])

    contact_x, contact_y = local_to_world(
        ship,
        closest_x,
        closest_y,
    )

    return nx, ny, penetration, contact_x, contact_y


# ============================================================
# PHYSICS: COLLISION RESPONSE
# ============================================================

def resolve_collision(ship, planet):
    collision = find_collision(ship, planet)

    if collision is None:
        return False

    nx, ny, penetration, contact_x, contact_y = collision

    ship.on_surface = True
    ship.surface_planet = planet

    rx = contact_x - ship.x
    ry = contact_y - ship.y

    # Velocity at the contact point includes angular velocity.
    contact_vx = ship.vx - ship.angular_velocity * ry
    contact_vy = ship.vy + ship.angular_velocity * rx

    normal_speed = contact_vx * nx + contact_vy * ny
    normal_impulse = 0.0

    if normal_speed < 0.0:
        cross_r_n = rx * ny - ry * nx

        effective_mass = (
            INV_MASS
            + cross_r_n**2 * INV_INERTIA
        )

        normal_impulse = (
            -(1.0 + RESTITUTION)
            * normal_speed
            / effective_mass
        )

        impulse_x = normal_impulse * nx
        impulse_y = normal_impulse * ny

        ship.vx += impulse_x * INV_MASS
        ship.vy += impulse_y * INV_MASS

        ship.angular_velocity += (
            rx * impulse_y - ry * impulse_x
        ) * INV_INERTIA

        # Friction impulse.
        contact_vx = ship.vx - ship.angular_velocity * ry
        contact_vy = ship.vy + ship.angular_velocity * rx

        tx = -ny
        ty = nx

        tangent_speed = contact_vx * tx + contact_vy * ty
        cross_r_t = rx * ty - ry * tx

        tangent_effective_mass = (
            INV_MASS
            + cross_r_t**2 * INV_INERTIA
        )

        tangent_impulse = (
            -tangent_speed / tangent_effective_mass
        )

        max_friction = FRICTION * normal_impulse

        tangent_impulse = max(
            -max_friction,
            min(max_friction, tangent_impulse),
        )

        friction_x = tangent_impulse * tx
        friction_y = tangent_impulse * ty

        ship.vx += friction_x * INV_MASS
        ship.vy += friction_y * INV_MASS

        ship.angular_velocity += (
            rx * friction_y - ry * friction_x
        ) * INV_INERTIA

    # Correct the overlap without deleting tangential motion.
    if penetration > 0.0:
        correction = penetration + 1e-5

        ship.x += nx * correction
        ship.y += ny * correction

    return True


# ============================================================
# PHYSICS: SIMULATE ONE SPACECRAFT
# ============================================================

def simulate_spacecraft(ship, world, dt, keys):
    rotation_input = (
        int(keys[pygame.K_RIGHT])
        - int(keys[pygame.K_LEFT])
    )

    ship.thrust_direction = (
        int(keys[pygame.K_UP])
        - int(keys[pygame.K_DOWN])
    )

    minimum_travel = max(1.0, ROCKET_WIDTH * 0.25)

    travel_steps = math.ceil(
        ship.speed * dt / minimum_travel
    )

    time_steps = math.ceil(
        dt / MAX_PHYSICS_STEP
    )

    steps = max(1, time_steps, travel_steps)
    steps = min(steps, 512)

    h = dt / steps

    for _ in range(steps):
        ship.on_surface = False
        ship.surface_planet = None

        # Angular controls.
        ship.angular_velocity += (
            rotation_input * ROTATION_ACCELERATION * h
        )

        if rotation_input == 0:
            ship.angular_velocity *= math.exp(
                -ANGULAR_DAMPING * h
            )

        # Gravity from each planet.
        ax = 0.0
        ay = 0.0

        for planet in world.planets:
            dx = planet.x - ship.x
            dy = planet.y - ship.y

            distance = math.hypot(dx, dy)
            safe_distance = max(distance, planet.radius)

            denominator = safe_distance**3

            ax += planet.mu * dx / denominator
            ay += planet.mu * dy / denominator

        # Engine thrust.
        if ship.thrust_direction != 0:
            thrust_acceleration = (
                ROCKET_THRUST_FORCE
                / ROCKET_MASS
                * ship.thrust_direction
            )

            ax += (
                thrust_acceleration * math.cos(ship.angle)
            )
            ay += (
                thrust_acceleration * math.sin(ship.angle)
            )

        # Semi-implicit Euler integration.
        ship.vx += ax * h
        ship.vy += ay * h

        ship.x += ship.vx * h
        ship.y += ship.vy * h

        ship.angle += ship.angular_velocity * h

        # Only planets collide with spacecraft.
        for planet in world.planets:
            resolve_collision(ship, planet)


def simulate_world(world, dt, keys):
    """Advance the physics and economy by one frame."""
    for ship in world.spacecraft:
        simulate_spacecraft(ship, world, dt, keys)

    world.update_economy(dt)


# ============================================================
# TRAJECTORY PREDICTION
# ============================================================

def predict_trajectory(ship, world):
    """
    Predict a future path using the current velocity and gravity.

    No player thrust or rotation input is applied. The real
    spacecraft and world remain unchanged.
    """

    x = ship.x
    y = ship.y
    vx = ship.vx
    vy = ship.vy

    angle = ship.angle
    angular_velocity = ship.angular_velocity

    points = [(x, y)]
    elapsed = 0.0

    while elapsed < TRAJECTORY_DURATION:
        dt = min(
            TRAJECTORY_STEP,
            TRAJECTORY_DURATION - elapsed,
        )

        ax = 0.0
        ay = 0.0

        for planet in world.planets:
            dx = planet.x - x
            dy = planet.y - y

            distance = math.hypot(dx, dy)
            safe_distance = max(distance, planet.radius)

            denominator = safe_distance**3

            ax += planet.mu * dx / denominator
            ay += planet.mu * dy / denominator

        # Predict passive flight with the engine off.
        vx += ax * dt
        vy += ay * dt

        x += vx * dt
        y += vy * dt

        angular_velocity *= math.exp(-ANGULAR_DAMPING * dt)
        angle += angular_velocity * dt

        points.append((x, y))
        elapsed += dt

        # Stop the predicted path if the actual rectangular
        # spacecraft shape would collide with a planet.
        predicted_ship = Spacecraft(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            angle=angle,
            angular_velocity=angular_velocity,
        )

        if any(
            find_collision(predicted_ship, planet) is not None
            for planet in world.planets
        ):
            break

    return points


def should_show_trajectory(ship, keys):
    if ship.on_surface:
        return False

    flight_controls = (
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_UP,
        pygame.K_DOWN,
    )

    return not any(keys[key] for key in flight_controls)


def draw_trajectory(ship, world):
    points = predict_trajectory(ship, world)

    if len(points) < 2:
        return

    screen_points = [
        camera.world_to_screen(x, y)
        for x, y in points
    ]

    pygame.draw.lines(
        screen,
        TRAJECTORY_COLOR,
        False,
        screen_points,
        max(1, round(camera.zoom * 1.5)),
    )

    # Small dotted markers along the forecast.
    marker_radius = max(1, round(2 * camera.zoom))

    for point in screen_points[::8]:
        pygame.draw.circle(
            screen,
            TRAJECTORY_COLOR,
            point,
            marker_radius,
        )


# ============================================================
# RESOURCE TRANSPORT
# ============================================================

def load_resources(world, ship, resource_key):
    """Load exactly 10 units of one selected resource."""

    if not ship.on_surface or ship.surface_planet is None:
        world.status_message = (
            "Cannot load: land on a planet first."
        )
        return

    planet = ship.surface_planet
    amount = RESOURCE_TRANSFER_AMOUNT

    if planet.resources[resource_key] < amount:
        world.status_message = (
            f"{planet.name}: need {amount} "
            f"{RESOURCE_TYPES[resource_key].name}; "
            f"have {planet.resources[resource_key]}."
        )
        return

    planet.resources[resource_key] -= amount
    ship.cargo[resource_key] += amount

    world.status_message = (
        f"Loaded {amount} {RESOURCE_TYPES[resource_key].name} "
        f"from {planet.name}."
    )


def unload_resources(world, ship):
    """Unload every carried resource onto the current planet."""

    if not ship.on_surface or ship.surface_planet is None:
        world.status_message = (
            "Cannot unload: land on a planet first."
        )
        return

    if ship.total_cargo == 0:
        world.status_message = "Rocket cargo is empty."
        return

    planet = ship.surface_planet
    unloaded_total = ship.total_cargo

    for resource_key in RESOURCE_KEYS:
        planet.resources[resource_key] += ship.cargo[resource_key]
        ship.cargo[resource_key] = 0

    world.status_message = (
        f"Unloaded {unloaded_total} resources onto {planet.name}."
    )


# ============================================================
# BUILDING PLACEMENT
# ============================================================

def angle_distance(a, b):
    return abs((a - b + math.pi) % TAU - math.pi)


def building_minimum_angle(planet):
    center_radius = planet.radius + BUILDING_HEIGHT / 2.0

    minimum_center_distance = (
        math.hypot(BUILDING_WIDTH, BUILDING_HEIGHT)
        + BUILDING_GAP
    )

    ratio = min(
        1.0,
        minimum_center_distance / (2.0 * center_radius),
    )

    return 2.0 * math.asin(ratio)


def find_building_angle(planet, preferred_angle, world):
    minimum_angle = building_minimum_angle(planet)

    occupied = [
        building.angle
        for building in world.buildings
        if building.planet is planet
    ]

    candidates = [preferred_angle % TAU]

    for occupied_angle in occupied:
        candidates.append(
            (
                occupied_angle
                - minimum_angle
                - 0.0001
            ) % TAU
        )

        candidates.append(
            (
                occupied_angle
                + minimum_angle
                + 0.0001
            ) % TAU
        )

    valid_candidates = [
        candidate
        for candidate in candidates
        if all(
            angle_distance(candidate, occupied_angle)
            >= minimum_angle
            for occupied_angle in occupied
        )
    ]

    if not valid_candidates:
        return None

    return min(
        valid_candidates,
        key=lambda angle: angle_distance(
            angle, preferred_angle
        ),
    )


def build_near_ship(world, ship, resource_key):
    if not ship.on_surface or ship.surface_planet is None:
        world.status_message = (
            "Cannot build: land on a planet first."
        )
        return

    # Construction costs must be paid with a single raw resource.
    if resource_key not in RAW_RESOURCE_KEYS:
        world.status_message = (
            "Building requires one raw resource type. "
            "Select Raw Blue, Raw Red, or Raw Green."
        )
        return

    planet = ship.surface_planet
    cost = world.building_cost(planet)

    if planet.resources[resource_key] < cost:
        world.status_message = (
            f"{planet.name}: need {cost} "
            f"{RESOURCE_TYPES[resource_key].name}; "
            f"have {planet.resources[resource_key]}. "
            "Resource types cannot be mixed."
        )
        return

    preferred_angle = math.atan2(
        ship.y - planet.y,
        ship.x - planet.x,
    )

    angle = find_building_angle(
        planet,
        preferred_angle,
        world,
    )

    if angle is None:
        world.status_message = (
            f"{planet.name}: no free building sites remain."
        )
        return

    planet.resources[resource_key] -= cost

    world.buildings.append(
        Building(
            planet=planet,
            angle=angle,
        )
    )

    world.status_message = (
        f"Built on {planet.name}: paid {cost} "
        f"{RESOURCE_TYPES[resource_key].name}."
    )


# ============================================================
# RESOURCE SELECTION UI
# ============================================================

def draw_resource_selector(world):
    """
    Draw seven clickable resource-selection buttons, plus
    Load x10 and Unload All action buttons.
    """

    global resource_button_rects
    global load_button_rect
    global unload_button_rect

    panel_width = min(430, screen.get_width() - 16)
    panel_width = max(220, panel_width)

    panel_x = screen.get_width() - panel_width - 8
    panel_y = 8

    columns = 4 if panel_width >= 360 else 2
    button_height = 35
    button_gap = 5
    margin = 10

    button_width = (
        panel_width
        - 2 * margin
        - (columns - 1) * button_gap
    ) // columns

    rows = math.ceil(len(RESOURCE_KEYS) / columns)

    title_height = 30
    grid_y = panel_y + title_height

    grid_height = (
        rows * button_height
        + (rows - 1) * button_gap
    )

    action_y = grid_y + grid_height + 8
    action_height = 30
    panel_height = (
        action_y - panel_y
        + action_height
        + margin
    )

    panel = pygame.Surface(
        (panel_width, panel_height),
        pygame.SRCALPHA,
    )

    panel.fill((5, 8, 18, 220))
    screen.blit(panel, (panel_x, panel_y))

    title = small_font.render(
        "SELECT RESOURCE  (keys 1-7)",
        True,
        (225, 230, 240),
    )

    screen.blit(
        title,
        (panel_x + margin, panel_y + 8),
    )

    resource_button_rects = {}

    for index, resource_key in enumerate(RESOURCE_KEYS):
        row = index // columns
        column = index % columns

        x = panel_x + margin + column * (
            button_width + button_gap
        )

        y = grid_y + row * (
            button_height + button_gap
        )

        rect = pygame.Rect(
            x,
            y,
            button_width,
            button_height,
        )

        resource_button_rects[resource_key] = rect

        is_selected = resource_key == selected_resource

        if is_selected:
            background = (48, 62, 82)
            border = RESOURCE_TYPES[resource_key].color
            border_width = 2
        else:
            background = (24, 32, 46)
            border = (70, 80, 95)
            border_width = 1

        pygame.draw.rect(
            screen,
            background,
            rect,
            border_radius=4,
        )

        pygame.draw.rect(
            screen,
            border,
            rect,
            border_width,
            border_radius=4,
        )

        icon_size = 14
        icon_center = (
            rect.x + 14,
            rect.centery,
        )

        draw_resource_icon(
            screen,
            resource_key,
            icon_center,
            icon_size,
            background,
        )

        label = small_font.render(
            RESOURCE_TYPES[resource_key].short_name,
            True,
            (240, 240, 245),
        )

        screen.blit(
            label,
            (
                rect.x + 25,
                rect.centery - label.get_height() // 2,
            ),
        )

    action_gap = 8
    action_width = (
        panel_width - 2 * margin - action_gap
    ) // 2

    load_button_rect = pygame.Rect(
        panel_x + margin,
        action_y,
        action_width,
        action_height,
    )

    unload_button_rect = pygame.Rect(
        panel_x + margin + action_width + action_gap,
        action_y,
        action_width,
        action_height,
    )

    pygame.draw.rect(
        screen,
        (35, 85, 65),
        load_button_rect,
        border_radius=4,
    )

    pygame.draw.rect(
        screen,
        (70, 150, 105),
        load_button_rect,
        1,
        border_radius=4,
    )

    pygame.draw.rect(
        screen,
        (80, 50, 45),
        unload_button_rect,
        border_radius=4,
    )

    pygame.draw.rect(
        screen,
        (170, 95, 75),
        unload_button_rect,
        1,
        border_radius=4,
    )

    load_text = small_font.render(
        "LOAD x10 [L]",
        True,
        (240, 245, 240),
    )

    unload_text = small_font.render(
        "UNLOAD ALL [U]",
        True,
        (245, 235, 230),
    )

    screen.blit(
        load_text,
        load_text.get_rect(center=load_button_rect.center),
    )

    screen.blit(
        unload_text,
        unload_text.get_rect(center=unload_button_rect.center),
    )


def handle_resource_ui_click(position, world):
    global selected_resource

    for resource_key, rect in resource_button_rects.items():
        if rect.collidepoint(position):
            selected_resource = resource_key

            world.status_message = (
                f"Selected {RESOURCE_TYPES[resource_key].name}. "
                "L loads 10; B builds with raw resources."
            )

            return True

    ship = world.player_ship

    if load_button_rect.collidepoint(position):
        load_resources(world, ship, selected_resource)
        return True

    if unload_button_rect.collidepoint(position):
        unload_resources(world, ship)
        return True

    return False


# ============================================================
# BACKGROUND
# ============================================================

rng = random.Random(42)

stars = [
    (
        rng.uniform(-10000, 10000),
        rng.uniform(-10000, 10000),
        rng.randint(100, 220),
    )
    for _ in range(800)
]


def draw_background():
    screen.fill(BACKGROUND_COLOR)

    for x, y, brightness in stars:
        sx, sy = camera.world_to_screen(x, y)

        if (
            0 <= sx < screen.get_width()
            and 0 <= sy < screen.get_height()
        ):
            pygame.draw.circle(
                screen,
                (brightness, brightness, brightness),
                (sx, sy),
                1,
            )


# ============================================================
# DRAW PLANETS
# ============================================================

def draw_planet(planet):
    sx, sy = camera.world_to_screen(
        planet.x,
        planet.y,
    )

    radius = max(
        1,
        round(planet.radius * camera.zoom),
    )

    pygame.draw.circle(
        screen,
        planet.color,
        (sx, sy),
        radius,
    )

    # Show the quantity of the currently selected resource.
    amount = planet.resources[selected_resource]

    draw_resource_icon(
        screen,
        selected_resource,
        (sx - 13, sy),
        12,
        planet.color,
    )

    text = str(amount)

    shadow = font.render(
        text,
        True,
        (15, 20, 30),
    )

    foreground = font.render(
        text,
        True,
        (255, 255, 255),
    )

    rect = foreground.get_rect(
        center=(sx + 12, sy)
    )

    screen.blit(shadow, rect.move(1, 1))
    screen.blit(foreground, rect)


# ============================================================
# DRAW BUILDINGS
# ============================================================

def get_building_corners(building):
    planet = building.planet
    angle = building.angle

    center_radius = (
        planet.radius + BUILDING_HEIGHT / 2.0
    )

    cx = planet.x + math.cos(angle) * center_radius
    cy = planet.y + math.sin(angle) * center_radius

    tangent_x = -math.sin(angle)
    tangent_y = math.cos(angle)

    normal_x = math.cos(angle)
    normal_y = math.sin(angle)

    local_corners = [
        (-BUILDING_WIDTH / 2, -BUILDING_HEIGHT / 2),
        ( BUILDING_WIDTH / 2, -BUILDING_HEIGHT / 2),
        ( BUILDING_WIDTH / 2,  BUILDING_HEIGHT / 2),
        (-BUILDING_WIDTH / 2,  BUILDING_HEIGHT / 2),
    ]

    corners = []

    for lx, ly in local_corners:
        wx = cx + tangent_x * lx + normal_x * ly
        wy = cy + tangent_y * lx + normal_y * ly

        corners.append((wx, wy))

    return corners


def draw_building(building):
    points = [
        camera.world_to_screen(x, y)
        for x, y in get_building_corners(building)
    ]

    pygame.draw.polygon(
        screen,
        (175, 175, 165),
        points,
    )

    pygame.draw.polygon(
        screen,
        (65, 65, 65),
        points,
        max(1, round(camera.zoom)),
    )


# ============================================================
# DRAW SPACECRAFT
# ============================================================

def draw_spacecraft(ship):
    local_corners = [
        (-HALF_LENGTH, -HALF_WIDTH),
        ( HALF_LENGTH, -HALF_WIDTH),
        ( HALF_LENGTH,  HALF_WIDTH),
        (-HALF_LENGTH,  HALF_WIDTH),
    ]

    hull_points = [
        camera.world_to_screen(
            *local_to_world(ship, x, y)
        )
        for x, y in local_corners
    ]

    # The flames are visual effects only.
    if ship.thrust_direction != 0:
        if ship.thrust_direction == 1:
            flame_x = -HALF_LENGTH
            direction = -1
        else:
            flame_x = HALF_LENGTH
            direction = 1

        outer_flame = [
            (flame_x, -HALF_WIDTH * 0.72),
            (flame_x + direction * 13.0, 0.0),
            (flame_x, HALF_WIDTH * 0.72),
        ]

        inner_flame = [
            (flame_x, -HALF_WIDTH * 0.40),
            (flame_x + direction * 8.0, 0.0),
            (flame_x, HALF_WIDTH * 0.40),
        ]

        pygame.draw.polygon(
            screen,
            (255, 100, 30),
            [
                camera.world_to_screen(
                    *local_to_world(ship, x, y)
                )
                for x, y in outer_flame
            ],
        )

        pygame.draw.polygon(
            screen,
            (255, 220, 80),
            [
                camera.world_to_screen(
                    *local_to_world(ship, x, y)
                )
                for x, y in inner_flame
            ],
        )

    # Orange rectangular hull.
    pygame.draw.polygon(
        screen,
        (255, 145, 40),
        hull_points,
    )

    # Red engine section at the rear.
    engine_depth = ROCKET_LENGTH * 0.22

    engine = [
        (-HALF_LENGTH, -HALF_WIDTH),
        (-HALF_LENGTH + engine_depth, -HALF_WIDTH),
        (-HALF_LENGTH + engine_depth, HALF_WIDTH),
        (-HALF_LENGTH, HALF_WIDTH),
    ]

    pygame.draw.polygon(
        screen,
        (225, 45, 45),
        [
            camera.world_to_screen(
                *local_to_world(ship, x, y)
            )
            for x, y in engine
        ],
    )

    pygame.draw.polygon(
        screen,
        (65, 45, 35),
        hull_points,
        max(1, round(camera.zoom)),
    )


# ============================================================
# STATUS HUD
# ============================================================

def draw_hud(world):
    ship = world.player_ship

    if ship.on_surface and ship.surface_planet is not None:
        state = f"LANDED: {ship.surface_planet.name}"
    else:
        state = "IN FLIGHT"

    lines = [
        "INTERPLANETARY COLONY SIMULATOR",
        "",
    ]

    if show_controls:
        lines.extend([
            "CAMERA",
            "WASD          Move camera",
            "Wheel         Zoom",
            "Middle drag   Pan camera",
            "",
            "SPACECRAFT",
            "Left/Right    Rotate",
            "Up            Forward thrust",
            "Down          Reverse thrust",
            "",
            "COLONY & CARGO",
            "B             Build",
            "L             Load selected resource x10",
            "U             Unload all cargo",
            "Click buttons Select resource / load / unload",
            "1-7           Select resource",
            "H             Hide/show controls",
            "R             Reset world",
            "ESC           Quit",
            "",
        ])

    lines.extend([
        f"State: {state}",
        f"Speed: {ship.speed:,.2f} units/s",
        f"Selected: {RESOURCE_TYPES[selected_resource].name}",
        f"Cargo total: {ship.total_cargo}",
        f"Buildings: {len(world.buildings)}",
        f"Zoom: {camera.zoom:.2f}x",
        "",
    ])

    if (
        ship.on_surface
        and ship.surface_planet is not None
        and selected_resource in RAW_RESOURCE_KEYS
    ):
        planet = ship.surface_planet

        lines.append(
            f"Build cost: {world.building_cost(planet)} "
            f"{RESOURCE_TYPES[selected_resource].name}"
        )
        lines.append("Pay in one raw resource only.")
        lines.append("")

    # Wrap potentially long feedback messages.
    status_lines = textwrap.wrap(
        world.status_message,
        width=47,
    )

    lines.extend(status_lines or [""])

    line_height = 17
    panel_width = 440
    panel_height = len(lines) * line_height + 16

    panel = pygame.Surface(
        (panel_width, panel_height),
        pygame.SRCALPHA,
    )

    panel.fill((5, 8, 18, 215))
    screen.blit(panel, (8, 8))

    y = 16

    for line in lines:
        if line:
            text_surface = font.render(
                line,
                True,
                (210, 220, 235),
            )

            screen.blit(text_surface, (18, y))

        y += line_height


# ============================================================
# RESOURCE DETAILS PANEL
# ============================================================

def draw_resource_details_panel(world):
    """
    Show the rocket cargo manifest and, while landed, the current
    planet's inventory and extraction probabilities.
    """

    ship = world.player_ship

    lines = [
        "ROCKET CARGO",
    ]

    for key in RESOURCE_KEYS:
        info = RESOURCE_TYPES[key]

        lines.append(
            f"{info.short_name:<10} {ship.cargo[key]:>5}"
        )

    if ship.on_surface and ship.surface_planet is not None:
        planet = ship.surface_planet

        lines.extend([
            "",
            f"{planet.name.upper()} INVENTORY / DENSITY",
        ])

        for key in RESOURCE_KEYS:
            info = RESOURCE_TYPES[key]
            quantity = planet.resources[key]
            probability = planet.resource_densities[key] * 100

            lines.append(
                f"{info.short_name:<10} "
                f"{quantity:>5}  {probability:>5.1f}%"
            )
    else:
        lines.extend([
            "",
            "Land on a planet to inspect",
            "its resource stock and densities.",
        ])

    line_height = 17
    panel_width = min(300, screen.get_width() - 16)
    panel_height = len(lines) * line_height + 16

    # Place below the upper-right resource selector.
    panel_x = screen.get_width() - panel_width - 8
    panel_y = 175

    panel = pygame.Surface(
        (panel_width, panel_height),
        pygame.SRCALPHA,
    )

    panel.fill((5, 8, 18, 215))
    screen.blit(panel, (panel_x, panel_y))

    y = panel_y + 8

    for line in lines:
        if line:
            surface = panel_font.render(
                line,
                True,
                (215, 225, 235),
            )

            screen.blit(
                surface,
                (panel_x + 10, y),
            )

        y += line_height


# ============================================================
# RENDER WORLD
# ============================================================

def render_world(world, keys):
    draw_background()

    ship = world.player_ship

    # Draw the prediction behind solid objects.
    if should_show_trajectory(ship, keys):
        draw_trajectory(ship, world)

    for planet in world.planets:
        draw_planet(planet)

    for building in world.buildings:
        draw_building(building)

    for spacecraft in world.spacecraft:
        draw_spacecraft(spacecraft)

    draw_hud(world)
    draw_resource_selector(world)
    draw_resource_details_panel(world)

    pygame.display.flip()


# ============================================================
# MAIN LOOP
# ============================================================

world = create_default_world()
running = True

RESOURCE_SELECT_KEYS = {
    pygame.K_1: RESOURCE_KEYS[0],
    pygame.K_2: RESOURCE_KEYS[1],
    pygame.K_3: RESOURCE_KEYS[2],
    pygame.K_4: RESOURCE_KEYS[3],
    pygame.K_5: RESOURCE_KEYS[4],
    pygame.K_6: RESOURCE_KEYS[5],
    pygame.K_7: RESOURCE_KEYS[6],
}


while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)

    # --------------------------------------------------------
    # 1. Process events
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_h:
                show_controls = not show_controls

            elif event.key in RESOURCE_SELECT_KEYS:
                selected_resource = RESOURCE_SELECT_KEYS[event.key]

                world.status_message = (
                    f"Selected "
                    f"{RESOURCE_TYPES[selected_resource].name}."
                )

            elif event.key == pygame.K_b:
                build_near_ship(
                    world,
                    world.player_ship,
                    selected_resource,
                )

            elif event.key == pygame.K_l:
                load_resources(
                    world,
                    world.player_ship,
                    selected_resource,
                )

            elif event.key == pygame.K_u:
                unload_resources(
                    world,
                    world.player_ship,
                )

            elif event.key == pygame.K_r:
                world = create_default_world()
                selected_resource = "raw_blue"

                camera.x = 0.0
                camera.y = 0.0
                camera.zoom = 0.75

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            camera.zoom_at(
                mouse_x,
                mouse_y,
                ZOOM_SPEED ** event.y,
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                # Left click: resource selection or transfer buttons.
                handle_resource_ui_click(
                    event.pos,
                    world,
                )

            elif event.button == 2:
                camera.dragging = True
                camera.last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                camera.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if camera.dragging:
                mouse_x, mouse_y = event.pos
                last_x, last_y = camera.last_mouse_pos

                camera.x -= (
                    (mouse_x - last_x) / camera.zoom
                )

                camera.y -= (
                    (mouse_y - last_y) / camera.zoom
                )

                camera.last_mouse_pos = event.pos

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                event.size,
                pygame.RESIZABLE,
            )

    # --------------------------------------------------------
    # 2. Continuous input
    # --------------------------------------------------------

    keys = pygame.key.get_pressed()

    dx = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
    dy = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

    if dx != 0 and dy != 0:
        dx *= 1.0 / math.sqrt(2)
        dy *= 1.0 / math.sqrt(2)

    camera.move(dx, dy, dt)

    # --------------------------------------------------------
    # 3. Advance simulation
    # --------------------------------------------------------

    simulate_world(world, dt, keys)

    # --------------------------------------------------------
    # 4. Render
    # --------------------------------------------------------

    render_world(world, keys)


pygame.quit()