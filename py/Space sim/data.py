
from __future__ import annotations

from dataclasses import dataclass, field
import math
import random


# ============================================================
# RESOURCE DEFINITIONS
# ============================================================

@dataclass(frozen=True)
class ResourceInfo:
    name: str
    short_name: str
    category: str
    color: tuple[int, int, int]
    shape: str


RESOURCE_TYPES = {
    # Raw resources
    "raw_blue": ResourceInfo(
        "Blue Raw", "Raw Blue", "raw",
        (65, 145, 255), "square"
    ),
    "raw_red": ResourceInfo(
        "Red Raw", "Raw Red", "raw",
        (245, 75, 75), "circle"
    ),
    "raw_green": ResourceInfo(
        "Green Raw", "Raw Green", "raw",
        (70, 210, 105), "triangle"
    ),

    # Refined resources
    "refined_blue": ResourceInfo(
        "Blue Refined", "Ref Blue", "refined",
        (65, 145, 255), "octagon"
    ),
    "refined_red": ResourceInfo(
        "Red Refined", "Ref Red", "refined",
        (245, 75, 75), "pentagon"
    ),
    "refined_green": ResourceInfo(
        "Green Refined", "Ref Green", "refined",
        (70, 210, 105), "torus"
    ),

    # Advanced resource
    "advanced_white": ResourceInfo(
        "White Star", "White Star", "advanced",
        (255, 255, 255), "star"
    ),
}

RESOURCE_KEYS = tuple(RESOURCE_TYPES.keys())

RAW_RESOURCE_KEYS = (
    "raw_blue",
    "raw_red",
    "raw_green",
)

RESOURCE_TRANSFER_AMOUNT = 10


def empty_inventory() -> dict[str, int]:
    """Create an inventory containing all resource types."""
    return {key: 0 for key in RESOURCE_KEYS}


def initial_inventory(resource_key: str) -> dict[str, int]:
    """Give a new planet 20 units of its starting raw resource."""
    inventory = empty_inventory()
    inventory[resource_key] = 20
    return inventory


# ============================================================
# GAME CONFIGURATION
# ============================================================

# Buildings
BUILDING_WIDTH = 22.0
BUILDING_HEIGHT = 12.0
BUILDING_GAP = 4.0

BASE_BUILDING_COST = 10
BUILDING_COST_INCREMENT = 1

# Each building produces one random resource per second.
BUILDING_PRODUCTION = 1.0

# Spacecraft
ROCKET_LENGTH = 36.0
ROCKET_WIDTH = 14.0
ROCKET_MASS = 1.0

HALF_LENGTH = ROCKET_LENGTH / 2.0
HALF_WIDTH = ROCKET_WIDTH / 2.0

ROCKET_INERTIA = ROCKET_MASS * (
    ROCKET_LENGTH**2 + ROCKET_WIDTH**2
) / 12.0

# Physics
ROCKET_THRUST_FORCE = 100.0
ROTATION_ACCELERATION = 5.0
ANGULAR_DAMPING = 0.7

RESTITUTION = 0.05
FRICTION = 0.65
MAX_PHYSICS_STEP = 1.0 / 240.0


# ============================================================
# PLANET
# ============================================================

@dataclass
class Planet:
    name: str

    # World coordinates
    x: float
    y: float

    # Physical properties
    radius: float
    mu: float

    color: tuple[int, int, int]

    # Inventory of each resource
    resources: dict[str, int] = field(
        default_factory=empty_inventory
    )

    # Probability weights for extracting each resource.
    # These are normalized to sum to 1.
    resource_densities: dict[str, float] = field(
        default_factory=dict
    )

    # Partial progress toward the next produced resource.
    production_progress: float = 0.0

    def __post_init__(self):
        # Ensure that all resource types exist in the inventory.
        for key in RESOURCE_KEYS:
            self.resources.setdefault(key, 0)

        # Supply equal probabilities if none were configured.
        if not self.resource_densities:
            self.resource_densities = {
                key: 1.0 / len(RESOURCE_KEYS)
                for key in RESOURCE_KEYS
            }

        for key in RESOURCE_KEYS:
            self.resource_densities.setdefault(key, 0.0)

        # Normalize probabilities so their sum is 1.
        for key in RESOURCE_KEYS:
            self.resource_densities[key] = max(
                0.0,
                float(self.resource_densities[key]),
            )

        total = sum(self.resource_densities.values())

        if total <= 0:
            raise ValueError(
                f"{self.name} must have at least one nonzero "
                "resource density."
            )

        self.resource_densities = {
            key: value / total
            for key, value in self.resource_densities.items()
        }


# ============================================================
# SPACECRAFT
# ============================================================

@dataclass
class Spacecraft:
    x: float
    y: float

    vx: float
    vy: float

    angle: float | None = None
    angular_velocity: float = 0.0

    # -1 = reverse, 0 = off, 1 = forward
    thrust_direction: int = 0

    on_surface: bool = False
    surface_planet: Planet | None = None

    # Resource cargo travels with the spacecraft.
    cargo: dict[str, int] = field(
        default_factory=empty_inventory
    )

    def __post_init__(self):
        if self.angle is None:
            self.angle = math.atan2(self.vy, self.vx)

        for key in RESOURCE_KEYS:
            self.cargo.setdefault(key, 0)

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    @property
    def total_cargo(self) -> int:
        return sum(self.cargo.values())


# ============================================================
# BUILDING
# ============================================================

@dataclass
class Building:
    planet: Planet
    angle: float


# ============================================================
# WORLD
# ============================================================

@dataclass
class World:
    planets: list[Planet] = field(default_factory=list)
    spacecraft: list[Spacecraft] = field(default_factory=list)
    buildings: list[Building] = field(default_factory=list)

    status_message: str = (
        "Land on a planet to build or transfer resources."
    )

    rng: random.Random = field(
        default_factory=lambda: random.Random(42),
        repr=False,
    )

    @property
    def player_ship(self) -> Spacecraft:
        if not self.spacecraft:
            raise RuntimeError("The world has no spacecraft.")

        return self.spacecraft[0]

    def count_buildings(self, planet: Planet) -> int:
        return sum(
            1
            for building in self.buildings
            if building.planet is planet
        )

    def building_cost(self, planet: Planet) -> int:
        """
        Cost is 10 + the existing building count on this planet.

        The whole cost must be paid in one raw resource type.
        """
        return (
            BASE_BUILDING_COST
            + BUILDING_COST_INCREMENT
            * self.count_buildings(planet)
        )

    def update_economy(self, dt: float) -> None:
        """
        Each building produces one resource per second.

        The resource type is randomly selected according to
        the density probabilities of its planet.
        """

        for planet in self.planets:
            building_count = self.count_buildings(planet)

            if building_count == 0:
                continue

            planet.production_progress += (
                building_count * BUILDING_PRODUCTION * dt
            )

            while planet.production_progress >= 1.0:
                resource_key = self.rng.choices(
                    RESOURCE_KEYS,
                    weights=[
                        planet.resource_densities[key]
                        for key in RESOURCE_KEYS
                    ],
                    k=1,
                )[0]

                planet.resources[resource_key] += 1
                planet.production_progress -= 1.0


# ============================================================
# INITIAL WORLD
# ============================================================

def create_default_world() -> World:
    """
    Create the initial solar system.

    Each planet has distinct resource densities and starts with
    20 units of a different raw resource.
    """

    planets = [
        Planet(
            name="Aurelia",
            x=0.0,
            y=0.0,
            radius=200.0,
            mu=1_000_000.0,
            color=(65, 125, 190),
            resources=initial_inventory("raw_blue"),
            resource_densities={
                "raw_blue": 0.45,
                "raw_red": 0.25,
                "raw_green": 0.15,
                "refined_blue": 0.06,
                "refined_red": 0.04,
                "refined_green": 0.04,
                "advanced_white": 0.01,
            },
        ),

        Planet(
            name="Verdant",
            x=-720.0,
            y=-220.0,
            radius=125.0,
            mu=500_000.0,
            color=(65, 150, 95),
            resources=initial_inventory("raw_green"),
            resource_densities={
                "raw_blue": 0.10,
                "raw_red": 0.20,
                "raw_green": 0.40,
                "refined_blue": 0.06,
                "refined_red": 0.04,
                "refined_green": 0.16,
                "advanced_white": 0.04,
            },
        ),

        Planet(
            name="Ember",
            x=720.0,
            y=220.0,
            radius=90.0,
            mu=250_000.0,
            color=(185, 95, 65),
            resources=initial_inventory("raw_red"),
            resource_densities={
                "raw_blue": 0.12,
                "raw_red": 0.35,
                "raw_green": 0.08,
                "refined_blue": 0.08,
                "refined_red": 0.15,
                "refined_green": 0.14,
                "advanced_white": 0.08,
            },
        ),
    ]

    # Initial circular orbit around Aurelia.
    home = planets[0]
    orbit_radius = home.radius + 150.0

    orbital_speed = math.sqrt(home.mu / orbit_radius)

    ship = Spacecraft(
        x=home.x + orbit_radius,
        y=home.y,
        vx=0.0,
        vy=orbital_speed,
    )

    return World(
        planets=planets,
        spacecraft=[ship],
    )