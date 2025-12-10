"""Module for representing locations."""

from typing import Any


class Location:
    """Class representing a location in a game.

    Attributes
    ----------
    name: str
        Unique name for the location.
    description: str
        Description of the location.
    destinations: dict of str: str
        Possible destinations to go from this location, with the key being the direction and the
        value the name of the destination.
    items: list of str
        Items present in the location.

    Parameters
    ----------
    name: str
        Unique name for the location.
    description: str
        Description of the location.
    destinations: dict of str: str or None
        Possible destinations to go from this location, with the key being the direction and the
        value the name of the destination. Empty or `None` for no destinations.
    items: list of str or None
        Items present in the location. Empty or `None` for no items.
    """

    def __init__(
        self,
        name: str,
        description: str,
        destinations: dict[str, str] | None = None,
        items: list[str] | None = None,
    ):
        self.name = name
        self.description = description
        self.destinations = destinations or {}
        self.items = items or []

    def __str__(self):
        return f"{self.name}: {self.description}"

    def __repr__(self):
        attributes_repr = (
            f"name={self.name},"
            f"description={self.description},"
            f"destinations={self.destinations},"
            f"items={self.items}"
        )
        return f"{type(self).__name__}({attributes_repr})"


def create_location(data: Any) -> Location:
    """Creates a `Location` from a dict-like object.

    The input could for example look like this:

    {
      "name": "ROOM",
      "description": "A room in the castle",
      "items": [
        "CHEST", "SKULL", "KEY"
      ],
      "destinations": {
        "NORTH": "HALL"
        "WEST": "CLOSET"
      }
    }

    Parameters
    ----------
    data: Any
        dict-like object with keys 'name' and 'description' with string values, and
        optionally 'items', with a list of string values, and 'destinations', a dict
        with string keys and values.
    """
    name = str(data.get("name")).strip()
    description = str(data.get("description")).strip()
    items = [str(item).strip() for item in data.get("items", [])]
    destinations = {
        str(k).strip(): str(v).strip()
        for (k, v) in data.get("destinations", {}).items()
    }

    return Location(name, description, destinations, items)
