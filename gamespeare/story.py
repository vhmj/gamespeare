"""Module for story related classes and functions."""

from dataclasses import dataclass

from gamespeare.ending import Ending, GoalBasedEnding, RandomEnding, TimeBasedEnding
from gamespeare.state import State
from gamespeare.utils import GameDataError, get_missing_entries, validate_string
from gamespeare.world import World


def validate_goal_based_ending(ending: GoalBasedEnding, world: World) -> None:
    """Validates the integrity of a goal based ending.

    Parameters
    ----------
    ending: GoalBasedEnding
        The ending to validate for a given world.
    world: World
        The `World` to relate to.

    Raises
    ------
    PlaybookError
        Raised if the ending contain obvious errors.
    """
    for missing_item_name in get_missing_entries(ending.items, world.items):
        raise GameDataError(f'Ending item "{missing_item_name}" does not exist.')
    if ending.location and ending.location not in world.locations:
        raise GameDataError(f'Ending location "{ending.location}" does not exist.')


def validate_time_based_ending(ending: TimeBasedEnding) -> None:
    """Validates the integrity of a goal based ending.

    Parameters
    ----------
    ending: TimeBasedEnding
        The ending to validate.

    Raises
    ------
    PlaybookError
        Raised if the ending contain obvious errors.
    """
    if ending.turn_limit < 1:
        raise GameDataError(f'Ending turn limit "{ending.turn_limit}" to low.')


def validate_random_ending(ending: RandomEnding) -> None:
    """Validates the integrity of a random ending.

    Parameters
    ----------
    ending: RandomEnding
        The ending to validate.

    Raises
    ------
    PlaybookError
        Raised if the ending contain obvious errors.
    """
    if ending.probability > 1.0 or ending.probability < 0.0:
        raise GameDataError(
            f'Ending probability "{ending.probability}" not in [0.0, 1.1].'
        )


@dataclass
class Story:
    """Class for story elements of the game.

    prologue: str
        Prologue text to get the game started.
    epilogue: str
        Epilogue text to finish the game.
    endings: list of Ending
        Possible endings to the game.
    """

    prologue: str
    epilogue: str
    endings: list[Ending]

    def get_ending(self, state: State) -> Ending | None:
        """Checks ending for a specific state.

        Parameters
        ----------
        state: State
            The `State` to check ending for.

        Returns
        -------
        Ending or None
            An ending that matches the supplied state, or None if no ending applied.
        """
        for potential_ending in self.endings:
            if potential_ending.evaluate(state):
                return potential_ending
        return None

    def validate(self, world: World) -> None:
        """Validates the integrity of a `Story`.

        Parameters
        ----------
        world: World
            The `World` to relate to.

        Raises
        ------
        PlaybookError
            Raised if the story contains obvious errors.
        """
        validate_string(self.prologue, "Prologue")
        validate_string(self.epilogue, "Epilogue")
        self._validate_endings(world)

    def _validate_endings(self, world: World) -> None:
        """Validates the integrity of the endings.

        Parameters
        ----------
        world: World
            The `World` to relate to.

        Raises
        ------
        PlaybookError
            Raised if the endings contain obvious errors.
        """
        if not self.endings:
            raise GameDataError("No endings!")

        for ending in self.endings:
            validate_string(ending.reason, "Ending")

            if isinstance(ending, GoalBasedEnding):
                validate_goal_based_ending(ending, world)
            elif isinstance(ending, TimeBasedEnding):
                validate_time_based_ending(ending)
            elif isinstance(ending, RandomEnding):
                validate_random_ending(ending)
