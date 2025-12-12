"""Module for unit testing the `item` module"""

import unittest

from gamespeare.item import (
    Item,
    ItemContainer,
    LockableContainerItem,
    create_item,
    create_items,
    create_lockable_container_item,
    get_item_by_name,
)


class TestItem(unittest.TestCase):
    """Class for testing `Item`"""

    def test_item_str(self) -> None:
        """Tests `__str__()`"""
        item = Item(name="1", description="Item 1", takeable=True)
        self.assertEqual(str(item), "1: Item 1")


class TestLockableContainerItem(unittest.TestCase):
    """Class for testing `LockableContainerItem`"""

    def test_lockable_container_item_str(self) -> None:
        """Tests `__str__()`"""
        container = LockableContainerItem(
            name="1", description="Container 1", takeable=False
        )
        self.assertEqual(str(container), "1: Container 1")


class TestItemContainer(unittest.TestCase):
    """Class for testing `ItemContainer`"""

    def setUp(self) -> None:
        self.items = [
            Item(name="1", description="Item 1", takeable=True),
            Item(name="2", description="Item 2", takeable=True),
            Item(name="3", description="Item 3", takeable=False),
        ]

    def test_item_container_init(self) -> None:
        """Tests ItemContainer()"""
        empty = ItemContainer()
        self.assertIsInstance(empty, ItemContainer)
        self.assertCountEqual(empty.items, [])

        nonempty = ItemContainer(self.items)
        self.assertIsInstance(nonempty, ItemContainer)
        self.assertCountEqual(nonempty.items, self.items)

    def test_contains_item(self) -> None:
        """Tests `contains_item()`"""
        container = ItemContainer(self.items.copy())
        for item in self.items:
            self.assertTrue(container.contains_item(item), f"{item}")
            self.assertTrue(container.contains_item(item.name), f"{item.name}")

        missing = Item(name="MISSING", description="Missing", takeable=True)
        self.assertFalse(container.contains_item(missing))
        self.assertFalse(container.contains_item(missing.name))

    def test_add_item(self) -> None:
        """Tests `add_item()`"""
        container = ItemContainer()

        for item in self.items:
            container.add_item(item)
        self.assertCountEqual(container.items, self.items)

        container.add_item(self.items[0])
        with self.assertRaises(ValueError):
            container.add_item(self.items[0], strict=True)

    def test_remove_item_by_item(self) -> None:
        """Tests `test_remove_item()` with `Item`"""
        container = ItemContainer(self.items.copy())
        remaining_items = self.items.copy()

        for item in self.items:
            container.remove_item(item)
            remaining_items.remove(item)
            self.assertCountEqual(container.items, remaining_items)

        container.remove_item(self.items[0])
        with self.assertRaises(ValueError):
            container.remove_item(self.items[0], strict=True)

    def test_remove_item_by_str(self) -> None:
        """Tests `test_remove_item()` with `str`"""
        container = ItemContainer(self.items.copy())
        remaining_items = self.items.copy()

        for item in self.items:
            container.remove_item(item.name)
            remaining_items.remove(item)
            self.assertCountEqual(container.items, remaining_items)

        container.remove_item(self.items[0].name)
        with self.assertRaises(ValueError):
            container.remove_item(self.items[0].name, strict=True)


class TestItemStatic(unittest.TestCase):
    """Class for testing the static functions of the `item` module"""

    def test_get_item_by_name(self) -> None:
        """Tests `test_get_item_by_name()`"""
        no_items: list[Item] = []

        with self.assertRaises(ValueError):
            get_item_by_name(no_items, "MISSING")

        item1 = Item("1", "Description of 1", takeable=True)
        item2 = Item("2", "Description of 2", takeable=False)
        item3 = Item("3", "Description of 3", takeable=True)
        item4 = Item("4", "Description of 4", takeable=True)
        item5 = LockableContainerItem(
            "5", "Description of 5", takeable=False, key=item3, items=[item4]
        )
        items = [item1, item2, item5]

        self.assertIs(get_item_by_name(items, "1"), item1)
        self.assertIs(get_item_by_name(items, "2"), item2)
        self.assertIs(get_item_by_name(items, "5"), item5)

        with self.assertRaises(ValueError):
            get_item_by_name(items, "MISSING")
        with self.assertRaises(ValueError):
            get_item_by_name(items, "3")
        with self.assertRaises(ValueError):
            get_item_by_name(items, "4")

    def test_create_item_valid(self) -> None:
        """Tests `test_create_item()` with valid data"""
        minimal_item = create_item({"name": "MINIMAL", "description": "Minimal"})
        self.assertIsInstance(minimal_item, Item)
        self.assertEqual(minimal_item.name, "MINIMAL")
        self.assertEqual(minimal_item.description, "Minimal")
        self.assertEqual(minimal_item.takeable, True)

        takeable_item = create_item(
            {"name": "TAKEABLE", "description": "Takeable", "takeable": True}
        )
        self.assertIsInstance(takeable_item, Item)
        self.assertEqual(takeable_item.name, "TAKEABLE")
        self.assertEqual(takeable_item.description, "Takeable")
        self.assertEqual(takeable_item.takeable, True)

        untakeable_item = create_item(
            {"name": "UNTAKEABLE", "description": "Untakeable", "takeable": False}
        )
        self.assertIsInstance(untakeable_item, Item)
        self.assertEqual(untakeable_item.name, "UNTAKEABLE")
        self.assertEqual(untakeable_item.description, "Untakeable")
        self.assertEqual(untakeable_item.takeable, False)

    def test_create_item_invalid(self) -> None:
        """Tests `test_create_item()` with invalid data"""
        with self.assertRaises(ValueError):
            create_item(None)

        with self.assertRaises(ValueError):
            create_item({})

        with self.assertRaises(ValueError):
            no_name = {"description": "No name"}
            create_item(no_name)

        with self.assertRaises(ValueError):
            no_description = {"name": "NO DESCRIPTION"}
            create_item(no_description)

    def test_create_lockable_container_item_valid(self) -> None:
        """Tests create_lockable_container_item() with valid data"""
        minimal_item = create_lockable_container_item(
            data={"name": "MINIMAL", "description": "Minimal"}
        )
        self.assertIsInstance(minimal_item, LockableContainerItem)
        self.assertEqual(minimal_item.name, "MINIMAL")
        self.assertEqual(minimal_item.description, "Minimal")
        self.assertEqual(minimal_item.takeable, False)
        self.assertIs(minimal_item.key, None)
        self.assertCountEqual(minimal_item.items, [])

        takeable_item = create_lockable_container_item(
            data={"name": "TAKEABLE", "description": "Takeable", "takeable": True}
        )
        self.assertIsInstance(takeable_item, LockableContainerItem)
        self.assertEqual(takeable_item.name, "TAKEABLE")
        self.assertEqual(takeable_item.description, "Takeable")
        self.assertEqual(takeable_item.takeable, True)
        self.assertIs(takeable_item.key, None)
        self.assertCountEqual(takeable_item.items, [])

        untakeable_item = create_lockable_container_item(
            data={"name": "UNTAKEABLE", "description": "Untakeable", "takeable": False}
        )
        self.assertIsInstance(untakeable_item, LockableContainerItem)
        self.assertEqual(untakeable_item.name, "UNTAKEABLE")
        self.assertEqual(untakeable_item.description, "Untakeable")
        self.assertEqual(untakeable_item.takeable, False)
        self.assertIs(untakeable_item.key, None)
        self.assertCountEqual(untakeable_item.items, [])

        with_key = create_lockable_container_item(
            data={"name": "WITH KEY", "description": "With key", "key": "MINIMAL"},
            items=[minimal_item],
        )
        self.assertIsInstance(with_key, LockableContainerItem)
        self.assertEqual(with_key.name, "WITH KEY")
        self.assertEqual(with_key.description, "With key")
        self.assertIs(with_key.takeable, False)
        self.assertIs(with_key.key, minimal_item)

        with_items = create_lockable_container_item(
            data={
                "name": "WITH ITEMS",
                "description": "With items",
                "items": ["MINIMAL", "TAKEABLE"],
            },
            items=[minimal_item, takeable_item],
        )
        self.assertIsInstance(with_items, LockableContainerItem)
        self.assertEqual(with_items.name, "WITH ITEMS")
        self.assertEqual(with_items.description, "With items")
        self.assertEqual(with_items.takeable, False)
        self.assertIs(with_items.key, None)
        self.assertCountEqual(with_items.items, [minimal_item, takeable_item])

        with_item_and_key = create_lockable_container_item(
            data={
                "name": "WITH ITEM AND KEY",
                "description": "With item and key",
                "key": "MINIMAL",
                "items": ["TAKEABLE"],
            },
            items=[minimal_item, takeable_item],
        )
        self.assertIsInstance(with_item_and_key, LockableContainerItem)
        self.assertEqual(with_item_and_key.name, "WITH ITEM AND KEY")
        self.assertEqual(with_item_and_key.description, "With item and key")
        self.assertEqual(with_item_and_key.takeable, False)
        self.assertIs(with_item_and_key.key, minimal_item)
        self.assertCountEqual(with_item_and_key.items, [takeable_item])

    def test_create_lockable_container_item_invalid(self) -> None:
        """Tests `create_lockable_container_item()` with invalid data"""
        with self.assertRaises(ValueError):
            create_lockable_container_item(None)

        with self.assertRaises(ValueError):
            create_lockable_container_item({})

        with self.assertRaises(ValueError):
            no_name = {"description": "No name"}
            create_lockable_container_item(no_name)

        with self.assertRaises(ValueError):
            no_description = {"name": "NO DESCRIPTION"}
            create_lockable_container_item(no_description)

        item1 = create_lockable_container_item({"name": "1", "description": "Item 1"})
        item2 = create_lockable_container_item({"name": "2", "description": "Item 2"})
        items: list[Item] = [item1, item2]

        with self.assertRaises(ValueError):
            invalid_key = {
                "name": "INVALID KEY",
                "description": "Invalid key",
                "key": "MISSING",
            }
            create_lockable_container_item(invalid_key, items)

        with self.assertRaises(ValueError):
            invalid_item = {
                "name": "INVALID KEY",
                "description": "Invalid key",
                "items": ["ITEM1", "ITEM2", "MISSING"],
            }
            create_lockable_container_item(invalid_item, items)

    def test_create_items_valid(self) -> None:
        """Tests `test_create_items()` with valid data"""
        no_items = create_items([])
        self.assertCountEqual(no_items.items, [])

        item1 = Item("ITEM1", "Item 1.", takeable=True)
        item2 = Item("ITEM2", "Item 2.", takeable=True)
        item3 = Item("ITEM3", "Item 3.", takeable=False)
        container1 = LockableContainerItem("CONTAINER1", "Container 1.", takeable=False)
        container2 = LockableContainerItem(
            "CONTAINER2", "Container 2.", takeable=True, key=item1
        )
        container3 = LockableContainerItem(
            "CONTAINER3", "Container 3.", takeable=False, items=[item1, item2]
        )
        container4 = LockableContainerItem(
            "CONTAINER4", "Container 4.", takeable=False, key=item1, items=[item2]
        )

        valid_items_data = [
            {
                "class": "ITEM",
                "name": item1.name,
                "description": item1.description,
            },
            {
                "class": "ITEM",
                "name": item2.name,
                "description": item2.description,
                "takeable": item2.takeable,
            },
            {
                "class": "ITEM",
                "name": item3.name,
                "description": item3.description,
                "takeable": item3.takeable,
            },
            {
                "class": "CONTAINER",
                "name": container1.name,
                "description": container1.description,
            },
            {
                "class": "CONTAINER",
                "name": container2.name,
                "description": container2.description,
                "takeable": container2.takeable,
                "key": "ITEM1",
            },
            {
                "class": "CONTAINER",
                "name": container3.name,
                "description": container3.description,
                "takeable": container3.takeable,
                "items": ["ITEM1", "ITEM2"],
            },
            {
                "class": "CONTAINER",
                "name": container4.name,
                "description": container4.description,
                "takeable": container4.takeable,
                "key": "ITEM1",
                "items": ["ITEM2"],
            },
        ]

        valid_items = create_items(valid_items_data)
        valid_items_ref = [
            item1,
            item2,
            item3,
            container1,
            container2,
            container3,
            container4,
        ]
        self.assertCountEqual(valid_items.items, valid_items_ref)

    def test_create_items_invalid(self) -> None:
        """Tests `test_create_items()` with invalid data"""
        with self.assertRaises(ValueError):
            create_items(None)

        with self.assertRaises(ValueError):
            no_list_data = {
                "class": "ITEM",
                "name": "ITEM",
                "description": "Item",
            }
            create_items(no_list_data)

        with self.assertRaises(ValueError):
            no_class = [
                {
                    "name": "ITEM1",
                    "description": "Item",
                }
            ]
            create_items(no_class)

        with self.assertRaises(ValueError):
            no_item_name = [
                {
                    "class": "ITEM",
                    "description": "Item",
                }
            ]
            create_items(no_item_name)

        with self.assertRaises(ValueError):
            no_item_description = [
                {
                    "class": "ITEM",
                    "name": "ITEM",
                }
            ]
            create_items(no_item_description)

        with self.assertRaises(ValueError):
            no_container_name = [
                {
                    "class": "CONTAINER",
                    "description": "Container",
                }
            ]
            create_items(no_container_name)

        with self.assertRaises(ValueError):
            no_container_description = [
                {
                    "class": "CONTAINER",
                    "name": "CONTAINER",
                }
            ]
            create_items(no_container_description)

        with self.assertRaises(ValueError):
            bad_container_key = [
                {
                    "class": "CONTAINER",
                    "name": "CONTAINER",
                    "description": "Container",
                    "key": "MISSING",
                }
            ]
            create_items(bad_container_key)

        with self.assertRaises(ValueError):
            bad_container_items = [
                {
                    "class": "CONTAINER",
                    "name": "CONTAINER",
                    "description": "Container",
                    "items": ["MISSING"],
                }
            ]
            create_items(bad_container_items)


if __name__ == "__main__":
    unittest.main()
