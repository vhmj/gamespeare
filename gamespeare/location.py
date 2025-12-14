"""Module for representing locations."""

from dataclasses import dataclass, field
from typing import Any, Iterable

from gamespeare.gameobject import GameObject, GameObjectContainer, GameObjectError
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

    def validate(self, valid_objects: Iterable[GameObject]):
        """Validates the integrity of location in relation to valid objects.

        Raises
        ------
        GameObjectError
            Raised if the location contains obvious errors.
        """
        for game_object in self.contents:
            if not game_object in valid_objects:
                raise GameObjectError(f"Alien game object: {game_object}")

        for destination in self.destinations.values():
            if not destination in valid_objects:
                raise GameObjectError(f"Alien destination: {destination}")


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
    items: Iterable[Item] | None = None,
    ignore_destinations: bool = False,
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
    data: Any
        dict-like object with keys 'name' and 'description' with string values, and
        optionally 'items', with a list of string values, and 'destinations', a dict
        with string keys and values.
    locations: iterable of Location
        Valid locations.
    items: Iterable of Item or None
        Valid items.
    ignore_destinations: bool
        Skips parsing the destination data if set to `True`.

    Raises
    ------
    ValueError
        Raised if `data` lacks required values or has incorrect values.
    """
    item_dict = {item.name: item for item in items or []}
    location_dict = {location.name: location for location in locations or []}

    try:
        name = data["name"]
        description = data["description"]
        contents: list[GameObject] = [
            item_dict[item_name] for item_name in data.get("items", [])
        ]
        if ignore_destinations:
            destinations = {}
        else:
            destinations = {
                direction: location_dict[destination]
                for (direction, destination) in data.get("destinations", {}).items()
            }
    except KeyError as e:
        raise ValueError("Missing key") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e

    return Location(
        name=name, description=description, contents=contents, destinations=destinations
    )


def create_locations(data: Any, items: Iterable[Item] | None) -> list[Location]:
    """Creates locations from an iterable of dict-like data.

    The key `class` is required, and the supported values are:

    * `LOCATION` - See `create_location()` for additional requirements.

    Parameters
    ----------
    data: Any
        An iterable of dict-like objects with the key `class` and additional
        item data.
    items: Iterable of Item or None
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
    locations = _create_destinationless_locations(data=data, items=items or [])
    _set_location_destinations(data=data, locations=locations)

    return locations.get_location_list()


def _create_destinationless_locations(
    data: Any, items: Iterable[Item]
) -> LocationContainer:
    locations = LocationContainer()

    for entry in data:
        location_class = entry.get("class")
        if location_class == "LOCATION":
            location = create_location(entry, items=items, ignore_destinations=True)
            locations.add_location(location=location, strict=True)
        else:
            raise ValueError(f"Unsupported location class: {location_class}")

    return locations


def _set_location_destinations(data: Any, locations: LocationContainer) -> None:
    location_dict = locations.get_location_dict()

    for entry in data:
        try:
            location_dict[entry["name"]].destinations = {
                direction: location_dict[destination]
                for (direction, destination) in entry.get("destinations", {}).items()
            }
        except KeyError as e:
            raise ValueError("Alien destination") from e
