"""Module for representing items."""

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass
class Item:
    """Class representing an item.

    Attributes
    ----------
    name: str
        Unique name of the item.
    description: str
        Description of the item.
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
    """

    name: str
    description: str
    takeable: bool

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


@dataclass
class ItemContainer:
    """Class representing something that contains items.

    Attributes
    ----------
    items: list of Item
        The contained items.
    """

    items: list[Item] = field(default_factory=list[Item])

    def contains_item(self, item: str | Item) -> bool:
        """Checks if an item is part of the container's contents.

        Parameters
        ----------
        item: str or Item
            The item to check if it is part of the contents, eiter `Item` or
            its name.

        Returns
        -------
        bool
            ´True´ if the item is part of the contents, ´False` otherwise.
        """
        if isinstance(item, Item):
            return item in self.items

        item_name = str(item)
        for candidate in self.items:
            if candidate.name == item_name:
                return True
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
        if self.contains_item(item):
            if strict:
                raise ValueError(f"Duplicate item: {item}")
        else:
            self.items.append(item)

        self.items.sort(key=lambda x: x.name)

    def remove_item(self, item: str | Item, strict: bool = False) -> None:
        """Removes an item from the container.

        Parameters
        ----------
        item: Item or str
            The item to remove, eiter `Item` or its name.
        strict: bool
            Error will be raised not present items if set to `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the item is not present.
        """
        if not self.contains_item(item):
            if strict:
                raise ValueError(f"Non-existing item: {item}")
        elif isinstance(item, Item):
            self.items.remove(item)
        else:
            item_name = str(item)
            for candidate in self.items:
                if candidate.name == item_name:
                    self.items.remove(candidate)
                    break


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
    items: list of Item
        The contained items.
        Inherited from `ItemContainer`.
    """

    key: Item | None = field(default=None)


def create_items(data: Any) -> ItemContainer:
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
    ItemContainer
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
                    container.add_item(create_item(entry))
                elif item_class == "CONTAINER":
                    container.add_item(
                        create_lockable_container_item(entry, container.items)
                    )
                else:
                    raise ValueError(f"Unsupported item class: {item_class}")
            except KeyError as e:
                raise ValueError("Missing item class") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e

    return container


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
            name=str(data["name"]).strip(),
            description=str(data["description"]).strip(),
            takeable=data.get("takeable", takeable_default),
        )
    except KeyError as e:
        raise ValueError("Missing key") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e


def create_lockable_container_item(
    data: Any, items: list[Item] | None = None, takeable_default: bool = False
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
    items: list of Item or None
        Items allowed to be inside the container, empty list or `None` for no
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

    key_name = str(data.get("key", "")).strip()
    if key_name:
        container_item.key = get_item_by_name(items, key_name)

    for item_name in {str(item).strip() for item in data.get("items", [])}:
        item = get_item_by_name(items, item_name)
        container_item.add_item(item, strict=True)

    return container_item


def get_item_by_name(items: ItemContainer | Iterable[Item] | None, name: str) -> Item:
    """Gets the item with a specific name.

    Parameters
    ----------
    items: ItemContainer or Iterable of Item or None
        Items to search
    name: str
        Name of the item to get.

    Returns
    -------
    Item
        The first item encountered named ´name´.

    Raises
    ------
    ValueError
        Raised if no item named ´name´ were present.
    """
    if not items:
        items_to_search = []
    elif isinstance(items, ItemContainer):
        items_to_search = list(items.items)
    else:
        items_to_search = list(items)

    for item in items_to_search:
        if item.name == name:
            return item

    raise ValueError(f"Item does not exist: {name}")
