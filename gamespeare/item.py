"""Module for representing items."""

from dataclasses import dataclass, field
from typing import Any, Iterable

from gamespeare.gameobject import GameObject, GameObjectContainer
from gamespeare.utils import GameDataError


@dataclass
class Item(GameObject):
    """Class representing an item.

    Attributes
    ----------
    name: str
        Unique name of the item.
        Inherited from `GameObject`
    description: str
        Description of the item.
        Inherited from `GameObject`
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
    """

    description: str
    takeable: bool

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def validate(self, valid_objects: Iterable[GameObject]):
        """Validates the integrity of the item in relation to valid game objects.

        Raises
        ------
        GameDataError
            Raised if the item contains obvious errors.
        """
        if not self in valid_objects:
            raise GameDataError(f"Illegal item: {self}")


@dataclass
class ItemContainer(GameObjectContainer):
    """Class representing something that contains items.

    Attributes
    ----------
    contents: list of GameObject
        The contained game objects.
        Inherited from `GameObjectContainer`.
    """

    def contains_item(self, item: str | Item) -> bool:
        """Checks if an item is part of the container's contents.

        Parameters
        ----------
        item: str or Item
            The item to check if it is part of the contents, either `Item` or
            its name.

        Returns
        -------
        bool
            `True` if the item is part of the contents, `False` otherwise.
        """
        try:
            return isinstance(self.get(item), Item)
        except ValueError:
            return False

    def add_item(self, item: Item, strict: bool = False) -> None:
        """Adds an item to the container.

        Parameters
        ----------
        item: Item
            The item to add.
        strict: bool
            Error will be raised for already present items if set to `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the item is already present.
        """
        self.add(item, strict)

    def remove_item(self, item: str | Item, strict: bool = False) -> None:
        """Removes an item from the container.

        Parameters
        ----------
        item: Item or str
            The item to remove, eiter `Item` or its name.
        strict: bool
            Error will be raised for not present items if set to `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the item is not present.
        """
        self.remove(item, strict)

    def get_item(self, item: str | Item) -> Item:
        """Gets an item from the container.

        Parameters
        ----------
        item: Item or str
            The item to get, eiter `Item` or its name.

        Returns
        -------
        Item
            The requested item.

        Raises
        ------
        ValueError
            Raised if the specified item is not present.
        """
        candidate = self.get(item)
        if isinstance(candidate, Item):
            return candidate
        raise ValueError(f"Missing item: {item}")

    def get_item_list(self) -> list[Item]:
        """Gets a list of contained items.

        Returns
        -------
        list of GameObject
            New list of items.
        """
        return [item for item in self.get_list() if isinstance(item, Item)]

    def get_item_dict(self) -> dict[str, Item]:
        """Gets a dictionary of contained items.

        Returns
        -------
        dict of str, Item
            New dict of items with the names as keys and items as values.
        """
        return {item.name: item for item in self.get_item_list()}


@dataclass
class LockableContainerItem(ItemContainer, Item):
    """Class representing an item that can contain other items and be locked.

    Attributes
    ----------
    name: str
        Unique name of the item.
        Inherited from `Item`.
    description: str
        Description of the item.
        Inherited from `Item`.
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
        Inherited from `Item`.
    key: Item or None
        The item representing the key, or `None` for no key required.
    contents: list of GameObject
        The contained game objects.
        Inherited from `ItemContainer`.
    """

    key: Item | None = field(default=None)

    def validate(self, valid_objects: Iterable[GameObject]):
        """Validates the integrity of the lockable item container in relation to valid objects.

        Raises
        ------
        GameDataError
            Raised if the lockable item container contains obvious errors.
        """
        if not self in valid_objects:
            raise GameDataError(f"Illegal lockable item container: {self}")

        for item in self.get_item_list():
            if not item in valid_objects:
                raise GameDataError(f"Illegal contained item: {self}")


def create_items(data: Any) -> list[Item]:
    """Creates items from an iterable of dict-like data.

    The key `class` is required, and its supported values are:

    * `ITEM` - See `create_item()` for additional requirements.
    * `CONTAINER` - See `create_lockable_container_item()` for additional requirements.

    All item names must be unique. Container items must be defined after any items they contain.

    Parameters
    ----------
    data: Any
        An iterable of dict-like objects with the key `class` and additional item data.

    Returns
    -------
    list of Item
        Items initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    container = ItemContainer()

    try:
        for entry in data:
            try:
                item_class = entry["class"]

                if item_class == "ITEM":
                    item = create_item(entry)
                elif item_class == "CONTAINER":
                    item = create_lockable_container_item(
                        entry, container.get_item_list()
                    )
                else:
                    raise ValueError(f"Unsupported item class: {item_class}")

                container.add_item(item)
            except KeyError as e:
                raise ValueError("Missing item class") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e

    return container.get_item_list()


def create_item(data: Any, takeable_default: bool = True) -> Item:
    """Creates an `Item` from a dict-like object.

    The input could for example look like this:

    {
      "name": "SKULL",
      "description": "Yorick's skull"
      "takeable": True
    }

    Parameters
    ----------
    data: Any
        dict-like object with keys 'name' and 'description' with string values,
        and optionally the key 'takeable' with bool value.
    takeable_default:
        Default value for `takeable`.

    Raises
    ------
    ValueError
        Raised if `data` lacks required values or has incorrect values.
    """
    try:
        return Item(
            name=data["name"],
            description=data["description"],
            takeable=data.get("takeable", takeable_default),
        )
    except KeyError as e:
        raise ValueError("Missing key") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e


def create_lockable_container_item(
    data: Any, items: Iterable[Item] | None = None, takeable_default: bool = False
) -> LockableContainerItem:
    """Creates an `LockableContainerItem` from a dict-like object.

    The input could for example look like this:

    {
      "name": "CHEST",
      "description": "A sturdy chest",
      "key": "KEY"
      "items": [
        "GIFT"
      ]
    }

    Parameters
    ----------
    data: Any
        dict-like object compatible with `create_item()` and optionally the key
        'key' with string value, and/or the key 'items' with a list of string
        values. The strings represent names of items.
    items: iterable of Item or None
        Items allowed to be inside the container, empty or `None` for no
        allowed items.
    takeable_default:
        Default value for `takeable`.

    Raises
    ------
    ValueError
        Raised if `data` lacks required values, has incorrect values, or uses
        names of items not explicitly allowed.
    """
    base_item = create_item(data, takeable_default=takeable_default)
    container_item = LockableContainerItem(
        name=base_item.name,
        description=base_item.description,
        takeable=base_item.takeable,
    )

    allowed_items = ItemContainer(list(items or []))
    key_name = data.get("key")
    if key_name:
        container_item.key = allowed_items.get_item(key_name)

    for item_name in data.get("items", []):
        item = allowed_items.get_item(item_name)
        container_item.add_item(item, strict=True)

    return container_item
