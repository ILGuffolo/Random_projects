class GameError(Exception):
    "Base class for all errors related to this game engine."

    def __init__(self, message):
        self.message = message

class IllegalMoveError(GameError):
    "Base class for error indicating player's input is valid, but not currently allowed."
    pass

class CantActivateError(IllegalMoveError):
    "Raised when player tries activating something that can't currently be activated."

    def __init__(self, message):
        if not message:
            raise ValueError("CantActivateError must contain a player-facing helpful message")
        else:
            super().__init__(message)
