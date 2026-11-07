
import pygame
import numpy as np
import sys

# ============================================================
# CONFIGURATION
# ============================================================

WIDTH, HEIGHT = 1100, 750

DEFAULT_COLS = 220
DEFAULT_ROWS = 150

FPS = 60

DIFFUSION = 0.16
BRUSH_RADIUS = 5
BRUSH_STRENGTH = 3.0

# New physics parameters
FORCE_STRENGTH = 2.0
FADE_RATE = 0.16
VELOCITY_DECAY = 1.8
MAX_VELOCITY = 8.0

BACKGROUND = (8, 9, 13)
UI_HEIGHT = 125

PALETTE = [
    (255, 35, 65),
    (30, 100, 255),
    (30, 255, 130),
    (255, 210, 30),
    (200, 40, 255),
    (255, 120, 25),
    (255, 255, 255),
]

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Diffusion - Fluid Pigment")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 15)

cols = DEFAULT_COLS
rows = DEFAULT_ROWS

# RGB pigment quantity
field = np.zeros((rows, cols, 3), dtype=np.float32)

# Velocity field, measured in grid cells per simulation step
velocity_x = np.zeros((rows, cols), dtype=np.float32)
velocity_y = np.zeros((rows, cols), dtype=np.float32)

running = True
paused = False

current_color = 0

brush_radius = BRUSH_RADIUS
diffusion = DIFFUSION
brush_strength = BRUSH_STRENGTH

force_strength = FORCE_STRENGTH
fade_rate = FADE_RATE

previous_mouse = None


# ============================================================
# GRID MANAGEMENT
# ============================================================

def resize_grid(new_cols, new_rows):
    global field, velocity_x, velocity_y
    global cols, rows

    new_cols = max(30, min(600, new_cols))
    new_rows = max(30, min(500, new_rows))

    x_indices = np.linspace(
        0, cols - 1, new_cols
    ).astype(int)

    y_indices = np.linspace(
        0, rows - 1, new_rows
    ).astype(int)

    field = field[y_indices][:, x_indices].copy()

    velocity_x = velocity_x[y_indices][:, x_indices].copy()
    velocity_y = velocity_y[y_indices][:, x_indices].copy()

    cols = new_cols
    rows = new_rows


# ============================================================
# PAINTING
# ============================================================

def get_brush(x, y):

    gx = int(x * cols / WIDTH)
    gy = int(y * rows / HEIGHT)

    radius = brush_radius

    x0 = max(0, gx - radius * 3)
    x1 = min(cols, gx + radius * 3 + 1)

    y0 = max(0, gy - radius * 3)
    y1 = min(rows, gy + radius * 3 + 1)

    if x0 >= x1 or y0 >= y1:
        return None

    xx, yy = np.meshgrid(
        np.arange(x0, x1),
        np.arange(y0, y1)
    )

    distance_sq = (xx - gx)**2 + (yy - gy)**2

    sigma = max(0.8, radius / 1.7)

    brush = np.exp(
        -distance_sq / (2 * sigma**2)
    ).astype(np.float32)

    return x0, x1, y0, y1, brush


def deposit(x, y, color):

    brush_data = get_brush(x, y)

    if brush_data is None:
        return

    x0, x1, y0, y1, brush = brush_data

    pigment = np.array(color, dtype=np.float32)

    field[y0:y1, x0:x1] += (
        brush[:, :, None] *
        pigment[None, None, :] *
        brush_strength
    )


# ============================================================
# DIRECTIONAL FORCE
# ============================================================

def inject_force(x, y, direction_x, direction_y, amount):

    brush_data = get_brush(x, y)

    if brush_data is None:
        return

    x0, x1, y0, y1, brush = brush_data

    # Add directional momentum to nearby cells.

    velocity_x[y0:y1, x0:x1] += (
        brush * direction_x * amount
    )

    velocity_y[y0:y1, x0:x1] += (
        brush * direction_y * amount
    )


def paint_line(start, end, color):

    if start is None:
        deposit(*end, color)
        return

    dx = end[0] - start[0]
    dy = end[1] - start[1]

    distance = np.sqrt(dx * dx + dy * dy)

    steps = max(1, int(distance / 3))

    # Convert mouse movement to grid coordinates.

    grid_dx = dx * cols / WIDTH
    grid_dy = dy * rows / HEIGHT

    grid_length = np.sqrt(
        grid_dx**2 + grid_dy**2
    )

    if grid_length > 0:

        direction_x = grid_dx / grid_length
        direction_y = grid_dy / grid_length

        # Force per brush stamp.
        # This makes force depend on drag speed/distance,
        # without excessively accumulating along long strokes.

        force_amount = (
            force_strength *
            min(1.0, distance / 3.0) *
            0.35
        )

    else:
        force_amount = 0

    for i in range(steps + 1):

        t = i / steps

        x = start[0] + dx * t
        y = start[1] + dy * t

        deposit(x, y, color)

        if force_amount > 0:
            inject_force(
                x, y,
                direction_x,
                direction_y,
                force_amount
            )


# ============================================================
# BILINEAR SAMPLING
# ============================================================

def sample_field(data, x, y):
    """
    Sample a 2D or 3D grid at floating-point coordinates.
    Uses bilinear interpolation.
    """

    x = np.clip(x, 0, cols - 1)
    y = np.clip(y, 0, rows - 1)

    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)

    x1 = np.minimum(x0 + 1, cols - 1)
    y1 = np.minimum(y0 + 1, rows - 1)

    fx = (x - x0)
    fy = (y - y0)

    if data.ndim == 3:
        fx = fx[:, :, None]
        fy = fy[:, :, None]

    a = data[y0, x0]
    b = data[y0, x1]
    c = data[y1, x0]
    d = data[y1, x1]

    top = a * (1 - fx) + b * fx
    bottom = c * (1 - fx) + d * fx

    return top * (1 - fy) + bottom * fy


# ============================================================
# ADVECTION
# ============================================================

def advect():
    """
    Move pigment according to the velocity field.

    Semi-Lagrangian advection:
    For each destination cell, look backward along
    the velocity field to find its previous concentration.

    This produces flowing and directional movement.
    """

    global field, velocity_x, velocity_y

    yy, xx = np.mgrid[0:rows, 0:cols]

    # Backtrace the position of each cell.

    previous_x = xx - velocity_x
    previous_y = yy - velocity_y

    # Move pigment.

    field = sample_field(
        field,
        previous_x,
        previous_y
    )

    # Move the velocity field itself too.
    # This helps produce more coherent motion.

    velocity_x = sample_field(
        velocity_x,
        previous_x,
        previous_y
    )

    velocity_y = sample_field(
        velocity_y,
        previous_x,
        previous_y
    )


# ============================================================
# DIFFUSION
# ============================================================

def diffuse():
    """
    Conservative pairwise diffusion.

    Every cell exchanges pigment with its neighbors.
    """

    global field

    d = diffusion

    change = np.zeros_like(field)

    # Horizontal exchanges

    flux_x = d * (
        field[:, :-1] - field[:, 1:]
    )

    change[:, :-1] -= flux_x
    change[:, 1:] += flux_x

    # Vertical exchanges

    flux_y = d * (
        field[:-1, :] - field[1:, :]
    )

    change[:-1, :] -= flux_y
    change[1:, :] += flux_y

    field += change


# ============================================================
# DISSIPATION
# ============================================================

def dissipate(dt):
    """
    Gradually remove pigment and momentum.

    Exponential decay makes fading independent of FPS.
    """

    global field, velocity_x, velocity_y

    color_decay = np.exp(-fade_rate * dt)

    velocity_decay = np.exp(
        -VELOCITY_DECAY * dt
    )

    field *= color_decay

    velocity_x *= velocity_decay
    velocity_y *= velocity_decay

    # Prevent excessive velocity.

    np.clip(
        velocity_x,
        -MAX_VELOCITY,
        MAX_VELOCITY,
        out=velocity_x
    )

    np.clip(
        velocity_y,
        -MAX_VELOCITY,
        MAX_VELOCITY,
        out=velocity_y
    )


# ============================================================
# SIMULATION
# ============================================================

def simulate(dt):

    # Semi-Lagrangian advection is stable for large
    # displacements, but smaller steps improve detail.

    substeps = max(1, int(np.ceil(dt / (1 / 60))))
    step_dt = dt / substeps

    for _ in range(substeps):

        # Scale velocities to the substep duration.

        velocity_x[:] *= step_dt * 60
        velocity_y[:] *= step_dt * 60

        advect()

        # Restore velocity scale for the next step.
        velocity_x[:] /= step_dt * 60
        velocity_y[:] /= step_dt * 60

        diffuse()

        dissipate(step_dt)


# ============================================================
# RENDERING
# ============================================================

def render():

    # Convert pigment quantity into visible color.

    exposure = 0.035

    rgb = 255.0 * (
        1.0 - np.exp(-field * exposure)
    )

    rgb = np.clip(
        rgb, 0, 255
    ).astype(np.uint8)

    surface = pygame.Surface((cols, rows))

    pygame.surfarray.blit_array(
        surface,
        np.transpose(rgb, (1, 0, 2))
    )

    scaled = pygame.transform.smoothscale(
        surface,
        (WIDTH, HEIGHT)
    )

    screen.blit(scaled, (0, 0))


# ============================================================
# INTERFACE
# ============================================================

def draw_ui():

    panel = pygame.Surface(
        (WIDTH, UI_HEIGHT),
        pygame.SRCALPHA
    )

    panel.fill((0, 0, 0, 165))

    screen.blit(panel, (0, 0))

    color = PALETTE[current_color]

    lines = [
        "COLOR DIFFUSION - FLUID PIGMENT",

        f"Grid: {cols} x {rows}    "
        f"Diffusion: {diffusion:.3f}    "
        f"Fade: {fade_rate:.2f}",

        f"Brush: {brush_radius}    "
        f"Strength: {brush_strength:.1f}    "
        f"Drag force: {force_strength:.1f}",

        "1-7: Colors    "
        "[ / ]: Brush size    "
        "- / +: Diffusion",

        "F / G: Increase/decrease fade    "
        "V / B: Increase/decrease force",

        ", / .: Resolution    "
        "SPACE: Pause    C: Clear    R: Reset    ESC: Quit",
    ]

    for i, line in enumerate(lines):

        text = font.render(
            line,
            True,
            (220, 225, 235)
        )

        screen.blit(
            text,
            (16, 9 + i * 19)
        )

    pygame.draw.rect(
        screen,
        color,
        (WIDTH - 55, 15, 35, 35),
        border_radius=6
    )


# ============================================================
# MAIN LOOP
# ============================================================

while running:

    dt = min(clock.tick(FPS) / 1000.0, 0.05)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_c:

                field.fill(0)
                velocity_x.fill(0)
                velocity_y.fill(0)

            elif event.key == pygame.K_r:

                field.fill(0)
                velocity_x.fill(0)
                velocity_y.fill(0)

                diffusion = DIFFUSION
                fade_rate = FADE_RATE
                force_strength = FORCE_STRENGTH

                brush_radius = BRUSH_RADIUS
                brush_strength = BRUSH_STRENGTH

            # Color selection

            elif pygame.K_1 <= event.key <= pygame.K_7:
                current_color = event.key - pygame.K_1

            # Brush size

            elif event.key == pygame.K_LEFTBRACKET:
                brush_radius = max(1, brush_radius - 1)

            elif event.key == pygame.K_RIGHTBRACKET:
                brush_radius = min(35, brush_radius + 1)

            # Diffusion

            elif event.key in (
                pygame.K_MINUS,
                pygame.K_KP_MINUS
            ):
                diffusion = max(
                    0.0, diffusion - 0.01
                )

            elif event.key in (
                pygame.K_EQUALS,
                pygame.K_PLUS,
                pygame.K_KP_PLUS
            ):
                diffusion = min(
                    0.24, diffusion + 0.01
                )

            # Fade

            elif event.key == pygame.K_f:
                fade_rate = min(
                    3.0, fade_rate + 0.05
                )

            elif event.key == pygame.K_g:
                fade_rate = max(
                    0.0, fade_rate - 0.05
                )

            # Directional force

            elif event.key == pygame.K_v:
                force_strength = min(
                    10.0, force_strength + 0.25
                )

            elif event.key == pygame.K_b:
                force_strength = max(
                    0.0, force_strength - 0.25
                )

            # Resolution

            elif event.key == pygame.K_COMMA:
                resize_grid(
                    int(cols * 0.8),
                    int(rows * 0.8)
                )

            elif event.key == pygame.K_PERIOD:
                resize_grid(
                    int(cols * 1.25),
                    int(rows * 1.25)
                )

    # ========================================================
    # MOUSE INPUT
    # ========================================================

    mouse_buttons = pygame.mouse.get_pressed()
    mouse_position = pygame.mouse.get_pos()

    if mouse_buttons[0]:

        if mouse_position[1] > UI_HEIGHT:

            paint_line(
                previous_mouse,
                mouse_position,
                PALETTE[current_color]
            )

            previous_mouse = mouse_position

    else:
        previous_mouse = None

    # ========================================================
    # PHYSICS
    # ========================================================

    if not paused:
        simulate(dt)

    # ========================================================
    # DRAW
    # ========================================================

    screen.fill(BACKGROUND)

    render()
    draw_ui()

    if paused:

        pause_text = font.render(
            "PAUSED",
            True,
            (255, 255, 255)
        )

        screen.blit(
            pause_text,
            (WIDTH // 2 - 35, HEIGHT - 35)
        )

    pygame.display.flip()


pygame.quit()
sys.exit()
