
import math
import colorsys
import pygame
import numpy as np

# ---------------------- SETTINGS ----------------------
WINDOW_SIZE = (1500, 820)
FPS = 60

MAX_PARTICLES = 400_000
SPACING = 0.1
LIFETIME = 5.0

MOUSE_RADIUS = 135
MOUSE_FORCE = 18.0
SWIRL_FORCE = 10
DRAG = 0.98

# Slightly higher resolution for smoother clouds.
RENDER_SCALE = 0.45

# Color-field behavior.
DIFFUSION = 5
INK_RETENTION = 0.995
INK_STRENGTH = 180.0
# ------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode(
    WINDOW_SIZE, pygame.RESIZABLE
)
pygame.display.set_caption("Liquid Dream")
clock = pygame.time.Clock()

W, H = screen.get_size()
GW = max(1, int(W * RENDER_SCALE))
GH = max(1, int(H * RENDER_SCALE))

glow = pygame.Surface((GW, GH)).convert()
field = np.zeros((GH, GW, 3), dtype=np.float32)
lap = np.empty_like(field)

capacity = MAX_PARTICLES
n = 0

# Preallocated particle arrays.
x = np.zeros(capacity, dtype=np.float32)
y = np.zeros(capacity, dtype=np.float32)
vx = np.zeros(capacity, dtype=np.float32)
vy = np.zeros(capacity, dtype=np.float32)
life = np.zeros(capacity, dtype=np.float32)
hues = np.zeros(capacity, dtype=np.float32)
phase = np.zeros(capacity, dtype=np.float32)

# Preallocated rendering buffers.
color_r = np.empty(capacity, dtype=np.float32)
color_g = np.empty(capacity, dtype=np.float32)
color_b = np.empty(capacity, dtype=np.float32)

hue = 0.0
elapsed = 0.0
last_mouse = None
running = True

# Saturated neon palette.
PALETTE_SIZE = 1024
palette = np.zeros((PALETTE_SIZE, 3), dtype=np.uint8)

for i in range(PALETTE_SIZE):
    h = i / PALETTE_SIZE
    r, g, b = colorsys.hsv_to_rgb(h, 0.92, 1.0)
    palette[i] = (
        int(r * 255), int(g * 255), int(b * 255)
    )


def resize_window(size):
    global W, H, GW, GH, glow, field, lap

    W, H = max(1, size[0]), max(1, size[1])
    GW = max(1, int(W * RENDER_SCALE))
    GH = max(1, int(H * RENDER_SCALE))

    glow = pygame.Surface((GW, GH)).convert()
    field = np.zeros((GH, GW, 3), dtype=np.float32)
    lap = np.empty_like(field)


def spawn_line(start, end, speed_x, speed_y):
    global n, hue

    x1, y1 = start
    x2, y2 = end

    distance = math.hypot(x2 - x1, y2 - y1)
    count = max(1, int(distance / SPACING) + 1)
    count = min(count, capacity - n)

    if count <= 0:
        return

    sl = slice(n, n + count)
    t = np.linspace(0, 1, count, dtype=np.float32)

    x[sl] = (
        x1 + (x2 - x1) * t
        + np.random.uniform(-1.5, 1.5, count)
    )
    y[sl] = (
        y1 + (y2 - y1) * t
        + np.random.uniform(-1.5, 1.5, count)
    )

    angles = np.random.uniform(0, math.tau, count)
    speeds = np.random.uniform(10, 80, count)

    vx[sl] = speed_x * 0.20 + np.cos(angles) * speeds
    vy[sl] = speed_y * 0.20 + np.sin(angles) * speeds

    life[sl] = np.random.uniform(5.0, LIFETIME, count)
    phase[sl] = np.random.uniform(0, math.tau, count)

    hues[sl] = (
        hue + np.random.uniform(-0.045, 0.045, count)
    ) % 1.0

    n += count


def reset():
    global n
    n = 0
    field.fill(0)


def diffuse_ink(dt):
    """Diffuse the color field with a stable 2D heat equation."""
    global field, lap

    lap.fill(0)

    lap[1:-1, 1:-1] = (
        field[:-2, 1:-1]
        + field[2:, 1:-1]
        + field[1:-1, :-2]
        + field[1:-1, 2:]
        - 4.0 * field[1:-1, 1:-1]
    )

    # No-flux edges.
    lap[0, 1:-1] = (
        field[1, 1:-1] + field[0, :-2]
        + field[0, 2:] - 3 * field[0, 1:-1]
    )
    lap[-1, 1:-1] = (
        field[-2, 1:-1] + field[-1, :-2]
        + field[-1, 2:] - 3 * field[-1, 1:-1]
    )
    lap[1:-1, 0] = (
        field[:-2, 0] + field[2:, 0]
        + field[1:-1, 1] - 3 * field[1:-1, 0]
    )
    lap[1:-1, -1] = (
        field[:-2, -1] + field[2:, -1]
        + field[1:-1, -2] - 3 * field[1:-1, -1]
    )

    lap[0, 0] = field[0, 1] + field[1, 0] - 2 * field[0, 0]
    lap[0, -1] = field[0, -2] + field[1, -1] - 2 * field[0, -1]
    lap[-1, 0] = field[-1, 1] + field[-2, 0] - 2 * field[-1, 0]
    lap[-1, -1] = field[-1, -2] + field[-2, -1] - 2 * field[-1, -1]

    # Faster spreading, while keeping the numerical step stable.
    diffusion_step = min(DIFFUSION * dt * 60, 0.20)
    field[:] += lap * diffusion_step
    field *= INK_RETENTION ** (dt * 60)

    np.clip(field, 0, 255, out=field)


def update_particles(dt, mouse):
    global n, field

    if n == 0:
        return

    life[:n] -= dt

    # Compact surviving particles in place.
    alive = life[:n] > 0
    count = int(np.count_nonzero(alive))

    if count < n:
        for arr in (x, y, vx, vy, life, hues, phase):
            arr[:count] = arr[:n][alive]
        n = count

    if n == 0:
        return

    # Ambient fluid-like motion.
    vx[:n] += np.sin(y[:n] * 0.006 + phase[:n] + elapsed) * 12 * dt
    vy[:n] += np.cos(x[:n] * 0.006 + phase[:n] + elapsed) * 12 * dt

    # Cursor force ONLY while drawing.
    if mouse is not None:
        mx, my = mouse
        dx = mx - x[:n]
        dy = my - y[:n]
        dist_sq = dx * dx + dy * dy

        ids = np.flatnonzero(
            (dist_sq < MOUSE_RADIUS ** 2) & (dist_sq > 1)
        )

        if len(ids):
            dist = np.sqrt(dist_sq[ids])
            nx = dx[ids] / dist
            ny = dy[ids] / dist
            strength = (1 - dist / MOUSE_RADIUS) ** 2

            vx[ids] += (
                nx * MOUSE_FORCE - ny * SWIRL_FORCE
            ) * strength * dt
            vy[ids] += (
                ny * MOUSE_FORCE + nx * SWIRL_FORCE
            ) * strength * dt

    vx[:n] *= DRAG ** (dt * 60)
    vy[:n] *= DRAG ** (dt * 60)

    np.clip(vx[:n], -1000, 1000, out=vx[:n])
    np.clip(vy[:n], -1000, 1000, out=vy[:n])

    x[:n] += vx[:n] * dt
    y[:n] += vy[:n] * dt

    # Bounce softly at the edges.
    outside_x = (x[:n] < 0) | (x[:n] >= W)
    outside_y = (y[:n] < 0) | (y[:n] >= H)

    vx[:n][outside_x] *= -0.7
    vy[:n][outside_y] *= -0.7

    np.clip(x[:n], 0, W - 1, out=x[:n])
    np.clip(y[:n], 0, H - 1, out=y[:n])

    # Deposit color into the diffusing field.
    px = np.clip(
        (x[:n] * RENDER_SCALE).astype(np.int32), 0, GW - 1
    )
    py = np.clip(
        (y[:n] * RENDER_SCALE).astype(np.int32), 0, GH - 1
    )
    idx = py * GW + px

    palette_idx = (
        (hues[:n] * PALETTE_SIZE).astype(np.int32)
        % PALETTE_SIZE
    )

    # Keep individual particle deposits very subtle.
    life_ratio = np.clip(life[:n] / LIFETIME, 0, 1)
    brightness = 0.015 + 0.055 * life_ratio

    color_r[:n] = palette[palette_idx, 0] * brightness
    color_g[:n] = palette[palette_idx, 1] * brightness
    color_b[:n] = palette[palette_idx, 2] * brightness

    # Accumulate particles into pixels efficiently.
    flat = field.reshape(-1, 3)

    flat[:, 0] += np.bincount(
        idx, weights=color_r[:n] * INK_STRENGTH / 255,
        minlength=GW * GH
    )
    flat[:, 1] += np.bincount(
        idx, weights=color_g[:n] * INK_STRENGTH / 255,
        minlength=GW * GH
    )
    flat[:, 2] += np.bincount(
        idx, weights=color_b[:n] * INK_STRENGTH / 255,
        minlength=GW * GH
    )

    np.clip(field, 0, 255, out=field)


while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.033)
    elapsed += dt
    hue = (hue + dt * 0.045) % 1.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                reset()
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
                resize_window(screen.get_size())

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                event.size, pygame.RESIZABLE
            )
            resize_window(event.size)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            last_mouse = event.pos

    mouse_pos = pygame.mouse.get_pos()
    drawing = pygame.mouse.get_pressed()[0]

    if drawing:
        if last_mouse is None:
            spawn_line(mouse_pos, mouse_pos, 0, 0)
        else:
            dx = mouse_pos[0] - last_mouse[0]
            dy = mouse_pos[1] - last_mouse[1]

            spawn_line(
                last_mouse, mouse_pos,
                dx / max(dt, 0.001),
                dy / max(dt, 0.001)
            )

        mouse = mouse_pos
        last_mouse = mouse_pos
    else:
        mouse = None
        last_mouse = None

    update_particles(dt, mouse)
    diffuse_ink(dt)

    # Render the diffused field smoothly.
    pixels = pygame.surfarray.pixels3d(glow)
    pixels[:] = np.clip(
        field.transpose(1, 0, 2), 0, 255
    ).astype(np.uint8)
    del pixels

    screen.fill((3, 4, 14))
    pygame.transform.smoothscale(glow, (W, H), screen)
    pygame.display.flip()

pygame.quit()
