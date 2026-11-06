
from dataclasses import dataclass
import random

from upgrades import UPGRADES
from Challenges import CHALLENGES


# --------------------------------------------------
# GAME STATE
# --------------------------------------------------

@dataclass
class GameState:
    gold: int = 0
    
    challenge_index: int = 0

    # Current challenge
    challenge_name: str = "The Goblin Gate"
    dice_sides: int = 20
    target: int = 20
    required_streak: int = 3

    # Current progress
    streak: int = 0
    best_streak: int = 0
    total_rolls: int = 0

    # Economy
    fail_reward: int = 10
    success_reward: int = 50
    
    # Player upgrades
    luck: float = 0.0
    roll_speed: float = 1.0


# --------------------------------------------------
# DICE
# --------------------------------------------------

class Dice:
    def __init__(self, sides: int):
        if sides < 2:
            raise ValueError("A die needs at least 2 sides.")

        self.sides = sides

    def roll(self) -> int:
        return random.randint(1, self.sides)


# --------------------------------------------------
# ROLL RESULT
# --------------------------------------------------

@dataclass
class RollResult:
    value: int
    success: bool
    critical_success: bool
    critical_failure: bool
    luck_proc: bool

    reward: int
    streak: int
    challenge_complete: bool


# --------------------------------------------------
# ROLL HANDLER
# --------------------------------------------------

class RollHandler:
    def __init__(self, state: GameState):
        self.state = state
        self.dice = Dice(state.dice_sides)

    def roll(self) -> RollResult:
        state = self.state

        value = self.dice.roll()
        state.total_rolls += 1

        critical_success = value == state.dice_sides
        critical_failure = value == 1

        luck_proc = False
        success = value >= state.target
        
        # Luck handler: if normal roll fails, there is % probability it will succed instead
        if not success and state.luck > 0:
            luck_proc = random.random() < state.luck

            if luck_proc:
                success = True
                value = state.dice_sides
        
        
        # -----------------------------
        # SUCCESS
        # -----------------------------
        if success:
            state.streak += 1
            state.best_streak = max(
                state.best_streak,
                state.streak
            )

            # Very simple combo reward for now.
            reward = state.success_reward * state.streak
            state.gold += reward

            challenge_complete = (
                state.streak >= state.required_streak
            )
            
            if challenge_complete:
                self.advance_challenge()

        # -----------------------------
        # FAILURE
        # -----------------------------
        else:
            state.streak = 0

            reward = state.fail_reward
            state.gold += reward

            challenge_complete = False

        return RollResult(
            value=value,
            success=success,
            critical_success=critical_success,
            critical_failure=critical_failure,
            luck_proc=luck_proc,
            reward=reward,
            streak=state.streak,
            challenge_complete=challenge_complete,
        )
    
    def buy_upgrade(self, index):
        if index < 0 or index >= len(UPGRADES):
            return False
        return UPGRADES[index].buy(self.state)
    
    
    def advance_challenge(self):
        state = self.state

        if state.challenge_index >= len(CHALLENGES) - 1:
            return False

        state.challenge_index += 1

        challenge = CHALLENGES[state.challenge_index]

        state.challenge_name = challenge["name"]
        state.required_streak = challenge["required_streak"]

        state.streak = 0

        return True



