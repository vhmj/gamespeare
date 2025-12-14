"""Module for representing locations."""

from dataclasses import dataclass, field
from typing import Any, Iterable

from gamespeare.gameobject import GameObject, GameObjectContainer
from gamespeare.item import Item, ItemContainer


@dataclass
class Location(ItemContainer, GameObject):
    """Class representing a location in a game.

    Attributes
    ----------
    name: str
        Unique name of the location.
        Inherited from `GameObject`
    description: str
        Description of the location.
        Inherited from `GameObject`
    contents: list of GameObject
        The contained game objects.
        Inherited from `GameObjectContainer`.
    destinations: dict of str: Location
        Possible destinations to go from this location, with the key being the direction and the
        value the destination location.
    """

    destinations: dict[str, Location] = field(default_factory=dict)


@dataclass
class LocationContainer(GameObjectContainer):
    """Class representing something that contains locations.

    Attributes
    ----------
    contents: list of GameObject
        The contained game objects.
        Inherited from `GameObjectContainer`.
    """

    def contains_location(self, location: str | Location) -> bool:
        """Checks if a location is part of the container's contents.

        Parameters
        ----------
        location: str or Location
            The location to check if it is part of the contents, either
            `Location` or its name.

        Returns
        -------
        bool
            `True` if the location is part of the contents, `False` otherwise.
        """
        try:
            return isinstance(self.get(location), Location)
        except ValueError:
            return False

    def add_location(self, location: Location, strict: bool = False) -> None:
        """Adds a location to the container.

        Parameters
        ----------
        location: Location
            The location to add.
        strict: bool
            Error will be raised for already present location if set to `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the location is already present.
        """
        self.add(location, strict)

    def remove_location(self, location: str | Location, strict: bool = False) -> None:
        """Removes a location from the container.

        Parameters
        ----------
        location: Location or str
            The location to remove, eiter `Location` or its name.
        strict: bool
            Error will be raised for not present locations if set to `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the location is not present.
        """
        self.remove(location, strict)

    def get_location(self, location: str | Location) -> Location:
        """Gets an item from the container.

        Parameters
        ----------
        location: Location or str
            The location to get, eiter `Location` or its name.

        Returns
        -------
        Location
            The requested location.

        Raises
        ------
        ValueError
            Raised if the specified location is not present.
        """
        candidate = self.get(location)
        if isinstance(candidate, Location):
            return candidate
        raise ValueError(f"Missing location: {location}")

    def get_location_list(self) -> list[Location]:
        """Gets a list of contained locations.

        Returns
        -------
        list of GameObject
            New list of locations.
        """
        return [loc for loc in self.get_list() if isinstance(loc, Location)]

    def get_location_dict(self) -> dict[str, Location]:
        """Gets a dictionary of contained locations.

        Returns
        -------
        dict of str, Location
            New dict of locations with the names as keys and locations as values.
        """
        return {loc.name: loc for loc in self.get_location_list()}


def create_location(
    data: Any,
    locations: Iterable[Location] | None = None,
    items: ItemContainer | Iterable[Item] | None = None,
) -> Location:
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
    items: ItemContainer or iterable of Item or None
        Valid items.
    locations: iterable of Location
        Valid locations.
    data: Any
        dict-like object with keys 'name' and 'description' with string values, and
        optionally 'items', with a list of string values, and 'destinations', a dict
        with string keys and values.

    Raises
    ------
    ValueError
        Raised if `data` lacks required values or has incorrect values.
    """
    if not items:
        valid_items = []
    elif isinstance(items, ItemContainer):
        valid_items = items.get_item_list()
    else:
        valid_items = list(items)
    item_dict = {item.name: item for item in valid_items}

    location_dict = {location.name: location for location in locations or []}

    try:
        name = str(data["name"]).strip()
        description = str(data["description"]).strip()
        contents: list[GameObject] = [
            item_dict[str(item).strip()] for item in data.get("items", [])
        ]
        destinations = {
            str(k).strip(): location_dict[str(v).strip()]
            for (k, v) in data.get("destinations", {}).items()
        }
    except KeyError as e:
        raise ValueError("Missing key") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e

    return Location(
        name=name, description=description, contents=contents, destinations=destinations
    )


def create_locations(
    data: Any, items: ItemContainer | Iterable[Item] | None
) -> list[Location]:
    """Creates locations from an iterable of dict-like data.

    The key `class` is required, and the supported values are:

    * `LOCATION` - See `create_location()` for additional requirements.

    Parameters
    ----------
    data: Any
        An iterable of dict-like objects with the key `class` and additional
        item data.
    items: ItemContainer or iterable of Item or None
        Valid items.

    Returns
    -------
    list of Location
        A list of locations initialized from `data`.


    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    locations = {}
    unfilled_destinations = {}

    for entry in data:
        location_class = entry.get("class")
        if location_class == "LOCATION":
            destinations = entry.pop("destinations", {})

            location = create_location(entry, items=items)
            if location.name in locations:
                raise ValueError(f"Duplicate location name: {location.name}")
            locations[location.name] = location

            if destinations:
                unfilled_destinations[location.name] = destinations
        else:
            raise ValueError(f"Unsupported ending class: {location_class}")

    for location_name, location_destinations in unfilled_destinations.items():
        location = locations[location_name]
        try:
            for raw_direction, raw_destination_name in location_destinations.items():

                direction = str(raw_direction).strip()
                destination_name = str(raw_destination_name).strip()

                if destination_name not in locations:
                    raise ValueError(f"Unknown destination: {destination_name}")

                location.destinations[direction] = locations[destination_name]
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid destination entry") from e

    return list(locations.values())
