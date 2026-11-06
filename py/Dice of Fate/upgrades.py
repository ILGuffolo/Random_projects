
from dataclasses import dataclass
from typing import Callable


@dataclass
class Upgrade:
    name: str
    description: str
    cost: int
    apply: Callable
    purchased: bool = False

    def buy(self, state):
        if self.purchased:
            return False

        if state.gold < self.cost:
            return False

        state.gold -= self.cost
        self.apply(state)
        self.purchased = True

        return True


# --------------------------------------------------
# UPGRADE EFFECTS
# --------------------------------------------------

def increase_luck(state):
    state.luck += 0.05
    
def increase_luck_big(state):
    state.luck += 0.15
    
def increase_luck_huge(state):
    state.luck += 0.25


def increase_failure_reward(state):
    state.fail_reward += 10


def increase_success_reward(state):
    state.success_reward += 50


def increase_roll_speed(state):
    state.roll_speed *= 1.25


# --------------------------------------------------
# AVAILABLE UPGRADES
# --------------------------------------------------

UPGRADES = [
    Upgrade(
        name="Lucky Charm",
        description="+5% chance to hit the target",
        cost=500,
        apply=increase_luck,
    ),
    
    Upgrade(
        name="Dragon's Favor",
        description="+15% chance to hit the target",
        cost=1250,
        apply=increase_luck_big,
    ),

    Upgrade(
        name="Pity Gold",
        description="+10 gold on every failure",
        cost=750,
        apply=increase_failure_reward,
    ),

    Upgrade(
        name="Greedy Dice",
        description="+50 gold on every success",
        cost=1000,
        apply=increase_success_reward,
    ),

    Upgrade(
        name="Faster Hands",
        description="25% faster rolls",
        cost=1500,
        apply=increase_roll_speed,
    ),
    
    Upgrade(
        name="Faking The Roll",
        description="+25% chance to hit the target",
        cost=10000,
        apply=increase_luck_huge,
    ),
]
