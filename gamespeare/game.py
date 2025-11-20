"""Module with the classes for representing an adventure game."""

from abc import ABC


class GameFileError(Exception):
    """Exception raised when a game file is invalid."""

    pass


class AdventureGame(ABC):
    """Class for representing an adventure game.

    Parameters
    ----------
    game_file : str
        Path to the game file to play.

    Raises
    --------
    GameFileError
        If the game file cannot be loaded.
    """

    def __init__(self, game_file: str) -> None:
        # TODO: Implement
        pass

    """Plays an adventure game."""

    def play(self) -> None:
        # TODO: Implement
        pass


class TextAdventureGame(AdventureGame):
    """Class for representing a text adventure game.

    Parameters
    ----------
    game_file : str
        Path to the game file to play.

    Raises
    --------
    GameFileError
        If the game file cannot be loaded.
    """

    def __init__(self, game_file: str) -> None:
        super().__init__(game_file)
