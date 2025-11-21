"""Module with the classes for representing an adventure game."""

import json
from abc import ABC
from json import JSONDecodeError
from typing import Any


class GameDataError(Exception):
    """Exception raised when game data is invalid.

    Attributes
    ----------
        message: str
            Explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class AdventureGame(ABC):
    """Class for representing an adventure game.

    Parameters
    ----------
    game_file : str
        Path to the game file to use.

    Raises
    --------
    GameDataError
        If the game file cannot be properly loaded.
    """

    def __init__(self, game_file: str) -> None:
        self._initialize_game_from_file(game_file)
        self._validate_initialized_game()

    def _initialize_game_from_file(self, game_file: str) -> None:
        """Initializes this `Game` based on data from a JSON file.

        Parameters
        ----------
        game_file : str
            Path to the JSON file to initialize this ´Game` with.

        Raises
        --------
        GameDataError
            If the JSON file cannot be properly loaded.
        """

        try:
            with open(game_file, mode="r", encoding="utf-8") as input_file:
                json_data = json.load(input_file)
        except JSONDecodeError as e:
            raise GameDataError("Invalid game file format.") from e
        except FileNotFoundError as e:
            raise GameDataError("Game file not found.") from e
        except OSError as e:
            raise GameDataError("Unable to load game file.") from e

        self._initialize_game_from_data(json_data)

    def _initialize_game_from_data(self, data: dict[str, Any]) -> None:
        """Initializes this `Game` based on supplied data.

        Parameters
        ----------
        data: dict
            Supports keys "start", "items", "locations", and "endings".
        """
        self._initialize_start(data.get("start"))
        self._initialize_items(data.get("items"))
        self._initialize_locations(data.get("locations"))
        self._initialize_endings(data.get("endings"))

    def _initialize_start(self, start: Any) -> None:
        """Initializes the start conditions of the game based on start data.

        Parameters
        ----------
        start: dict
            Start conditions of the game.

        Raises
        ------
        GameDataError
            If the start conditions contains errors or are missing.
        """

    def _initialize_items(self, items: Any) -> None:
        """Initializes items in the game based on the supplied item data.

        Parameters
        ----------
        items: list of dict
            List of items to add to the game.

        Raises
        ------
        GameDataError
            If the items contains errors.
        """

    def _initialize_locations(self, locations: Any) -> None:
        """Initializes locations in the game based on the supplied location data.

        Parameters
        ----------
        locations: list of dict
            List of locations to add to the game.

        Raises
        ------
        GameDataError
            If the locations contains errors.
        """

    def _initialize_endings(self, endings: Any) -> None:
        """Initializes endings of the game based on the supplied ending data.

        Parameters
        ----------
        endings: list of dict
            List of endings to add to the game.

        Raises
        ------
        GameDataError
            If the endings contains errors.
        """

    def _validate_initialized_game(self) -> None:
        """Validates the integrity of an initialized `Game`.

        Raises
        ------
        GameDataError
            If the initializes `Game` contains obvious errors.
        """

    def play(self) -> None:
        """Plays an adventure game."""
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
    GameDataError
        If the game file cannot be loaded.
    """

    def __init__(self, game_file: str) -> None:
        super().__init__(game_file)
