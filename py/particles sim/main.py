
import time
import random

import numpy as np
import pygame


# ============================================================
# CONFIGURATION
# ============================================================

WIDTH, HEIGHT = 1600, 1000
PARTICLE_COUNT = 500_000       # Try 100_000, then 250_000+
FPS = 60

GRAVITY = 0.003
MAX_SPEED = 7.0

# Percentage of velocity retained per nominal frame.
# 0.997 means 0.3% velocity loss per frame.
# Fast particles lose more absolute speed than slow particles.
DRAG = 0.9985

TRAIL_FADE_ALPHA = 12
COLOR_SPEED_MAX = 5.0

BACKGROUND = (4, 5, 7)


# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.DOUBLEBUF,
)
pygame.display.set_caption("Gravity Painter")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 23)

trail_surface = pygame.Surface(
    (WIDTH, HEIGHT)
).convert()
trail_surface.fill(BACKGROUND)

pixel_surface = pygame.Surface(
    (WIDTH, HEIGHT)
).convert()
pixel_surface.fill((0, 0, 0))

# Allocate the fade overlay only once.
fade_surface = pygame.Surface(
    (WIDTH, HEIGHT)
).convert()
fade_surface.fill(BACKGROUND)


# ============================================================
# WARM, MUTED SPEED-BASED PALETTE
# ============================================================

COLOR_STOPS = np.array(
    [
        [19, 23, 29],      # Almost-black blue-gray
        [34, 39, 43],      # Charcoal
        [58, 60, 57],      # Muted gray-olive
        [91, 78, 63],      # Earthy brown
        [132, 105, 78],    # Dusty amber
        [171, 143, 112],   # Warm sand
        [205, 184, 153],   # Soft ivory
    ],
    dtype=np.float32,
)


def make_palette(size=1024):
    positions = np.linspace(
        0, len(COLOR_STOPS) - 1, size
    )

    left = positions.astype(np.int32)
    right = np.minimum(
        left + 1, len(COLOR_STOPS) - 1
    )
    fraction = (positions - left)[:, None]

    colors = (
        COLOR_STOPS[left] * (1.0 - fraction)
        + COLOR_STOPS[right] * fraction
    )

    return np.clip(colors, 0, 255).astype(np.uint8)


PALETTE = make_palette()


# ============================================================
# PARTICLE ARRAYS
# ============================================================

rng = np.random.default_rng()

x = np.empty(PARTICLE_COUNT, dtype=np.float32)
y = np.empty(PARTICLE_COUNT, dtype=np.float32)
vx = np.empty(PARTICLE_COUNT, dtype=np.float32)
vy = np.empty(PARTICLE_COUNT, dtype=np.float32)

# Reusable buffers reduce repeated allocations.
px = np.empty(PARTICLE_COUNT, dtype=np.int32)
py = np.empty(PARTICLE_COUNT, dtype=np.int32)

speed_sq = np.empty(PARTICLE_COUNT, dtype=np.float32)
speed = np.empty(PARTICLE_COUNT, dtype=np.float32)
color_indices = np.empty(PARTICLE_COUNT, dtype=np.int32)


def initialize_particles():
    x[:] = rng.uniform(0, WIDTH, PARTICLE_COUNT)
    y[:] = rng.uniform(0, HEIGHT, PARTICLE_COUNT)

    # All particles begin stationary.
    vx.fill(0.0)
    vy.fill(0.0)


initialize_particles()


# ============================================================
# GRAVITY WELLS
# ============================================================

wells = []
temporary_well = None


def add_well(pos):
    wells.append({
        "x": float(pos[0]),
        "y": float(pos[1]),
        "mass": random.choice([400, 700, 1100]),
    })


def remove_nearest_well(pos):
    if not wells:
        return

    mx, my = pos

    index = min(
        range(len(wells)),
        key=lambda i: (
            (wells[i]["x"] - mx) ** 2
            + (wells[i]["y"] - my) ** 2
        ),
    )

    wells.pop(index)


def clear_trails():
    trail_surface.fill(BACKGROUND)


# ============================================================
# VECTORIZED PHYSICS
# ============================================================

def apply_well(well, dt):
    # Attraction toward one well, applied to every particle.
    dx = well["x"] - x
    dy = well["y"] - y

    dist_sq = dx * dx + dy * dy + 400.0
    acceleration = well["mass"] * GRAVITY / dist_sq

    vx[:] += dx * acceleration * dt
    vy[:] += dy * acceleration * dt


def update_particles(dt):
    global speed_sq, speed

    dt = min(dt, 2.0)

    # Gravity is applied before drag so active forces can
    # continuously re-accelerate particles.
    for well in wells:
        apply_well(well, dt)

    if temporary_well is not None:
        apply_well(temporary_well, dt)

    # Exponential, frame-rate-adjusted drag.
    # Velocity is reduced by a percentage, not a fixed amount.
    drag_factor = DRAG ** dt
    vx[:] *= drag_factor
    vy[:] *= drag_factor

    # Cap speed to keep the simulation stable.
    np.multiply(vx, vx, out=speed_sq)
    np.multiply(vy, vy, out=speed)
    speed_sq += speed

    too_fast = speed_sq > MAX_SPEED * MAX_SPEED

    if np.any(too_fast):
        scale = MAX_SPEED / np.sqrt(speed_sq[too_fast])
        vx[too_fast] *= scale
        vy[too_fast] *= scale

    # Integrate positions.
    x[:] += vx * dt
    y[:] += vy * dt

    # Wrap particles around the canvas.
    np.remainder(x, WIDTH, out=x)
    np.remainder(y, HEIGHT, out=y)

    # Ensure float-to-integer conversion never hits WIDTH/HEIGHT.
    np.minimum(
        x,
        np.nextafter(np.float32(WIDTH), np.float32(0)),
        out=x,
    )
    np.minimum(
        y,
        np.nextafter(np.float32(HEIGHT), np.float32(0)),
        out=y,
    )


# ============================================================
# PARTICLE RENDERING
# ============================================================

def draw_particles():
    global speed_sq, speed

    # Speed determines color.
    np.multiply(vx, vx, out=speed_sq)
    np.multiply(vy, vy, out=speed)
    speed_sq += speed
    np.sqrt(speed_sq, out=speed)

    np.multiply(
        speed,
        (len(PALETTE) - 1) / COLOR_SPEED_MAX,
        out=speed,
    )
    np.clip(
        speed, 0, len(PALETTE) - 1, out=speed
    )
    np.copyto(color_indices, speed, casting="unsafe")

    # Convert positions to valid pixel coordinates.
    np.copyto(px, x, casting="unsafe")
    np.copyto(py, y, casting="unsafe")
    np.clip(px, 0, WIDTH - 1, out=px)
    np.clip(py, 0, HEIGHT - 1, out=py)

    colors = PALETTE[color_indices]

    # Clear and populate the particle layer.
    pixel_surface.fill((0, 0, 0))

    pixels = pygame.surfarray.pixels3d(pixel_surface)
    pixels[px, py] = colors
    del pixels

    # Additive blending makes trajectories accumulate.
    trail_surface.blit(
        pixel_surface,
        (0, 0),
        special_flags=pygame.BLEND_RGB_ADD,
    )


def fade_trails():
    # Multiply the image by a factor slightly below 1.
    # This reuses the existing surface and avoids allocating
    # a new overlay every frame.
    trail_surface.blit(
        fade_surface,
        (0, 0),
        special_flags=pygame.BLEND_RGB_MULT,
    )


# ============================================================
# UI
# ============================================================

def draw_wells():
    for well in wells:
        pos = (int(well["x"]), int(well["y"]))
        pygame.draw.circle(
            screen, (105, 105, 100), pos, 11, 1
        )
        pygame.draw.circle(
            screen, (195, 180, 155), pos, 2
        )

    if temporary_well is not None:
        pos = (
            int(temporary_well["x"]),
            int(temporary_well["y"]),
        )
        pygame.draw.circle(
            screen, (150, 120, 90), pos, 15, 1
        )
        pygame.draw.circle(
            screen, (205, 185, 155), pos, 3
        )


def draw_hud(fps):
    lines = [
        f"Particles: {PARTICLE_COUNT:,} | "
        f"Wells: {len(wells)} | FPS: {fps:.0f}",
        "Hold LMB: temporary well | SPACE: permanent well",
        "RMB: remove well | P: pause | C: clear | R: reset",
        "S: save PNG | ESC: quit",
    ]

    for i, line in enumerate(lines):
        label = font.render(
            line, True, (145, 145, 140)
        )
        screen.blit(label, (12, 12 + i * 22))


# ============================================================
# MAIN LOOP
# ============================================================

running = True
paused = False
last_time = time.perf_counter()

while running:
    now = time.perf_counter()
    dt = min((now - last_time) * FPS, 2.0)
    last_time = now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                remove_nearest_well(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                add_well(pygame.mouse.get_pos())

            elif event.key == pygame.K_p:
                paused = not paused

            elif event.key == pygame.K_c:
                clear_trails()

            elif event.key == pygame.K_r:
                initialize_particles()
                wells.clear()
                temporary_well = None
                clear_trails()

            elif event.key == pygame.K_s:
                filename = f"gravity_{int(time.time())}.png"
                pygame.image.save(trail_surface, filename)
                print(f"Saved {filename}")

    # Temporary well follows the cursor while LMB is held.
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        temporary_well = {
            "x": float(mx),
            "y": float(my),
            "mass": 700,
        }
    else:
        temporary_well = None

    if not paused:
        update_particles(dt)
        fade_trails()
        draw_particles()

    screen.blit(trail_surface, (0, 0))
    draw_wells()
    draw_hud(clock.get_fps())

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
