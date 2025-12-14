"""Module for testing of endings."""

import random
import unittest

from gamespeare.ending import (
    GoalBasedEnding,
    RandomEnding,
    TimeBasedEnding,
    create_goal_based_ending,
    create_random_ending,
    create_time_based_ending,
)
from gamespeare.item import Item, ItemContainer
from gamespeare.location import Location
from gamespeare.state import State
from gamespeare.world import World


class TestRandomEnding(unittest.TestCase):
    """Tests RandomEnding"""

    def setUp(self) -> None:
        self.location = Location(name="TEST", description="Test location")
        self.state = State(turn_no=1, location=self.location)

        random.seed(1234)

    def test_random_ending(self) -> None:
        """Tests RandomEnding.evaluate() with p=0.4"""

        ending = RandomEnding(reason="Test", probability=0.4)
        self.assertEqual(True, ending.evaluate(self.state))
        self.assertEqual(False, ending.evaluate(self.state))
        self.assertEqual(False, ending.evaluate(self.state))
        self.assertEqual(True, ending.evaluate(self.state))
        self.assertEqual(True, ending.evaluate(self.state))
        self.assertEqual(False, ending.evaluate(self.state))

    def test_random_ending_always(self) -> None:
        """Tests RandomEnding.evaluate() with p=1.0"""
        ending = RandomEnding(reason="Test", probability=1.0)

        for _ in range(10000):
            self.assertEqual(True, ending.evaluate(self.state))

    def test_random_ending_never(self) -> None:
        """Tests RandomEnding.evaluate() with p=0.0"""
        ending = RandomEnding(reason="Test", probability=0.0)

        for _ in range(10000):
            self.assertEqual(False, ending.evaluate(self.state))

    def test_create_random_ending_valid(self) -> None:
        """Tests create_random_ending() with valid data"""
        ending = create_random_ending({"reason": "Reason", "probability": 0.1337})
        self.assertIsInstance(ending, RandomEnding)
        self.assertEqual(ending.reason, "Reason")
        self.assertAlmostEqual(ending.probability, 0.1337)

    def test_create_random_ending_invalid(self) -> None:
        """Tests create_random_ending() with invalid data"""
        with self.assertRaises(ValueError):
            create_random_ending({})

        with self.assertRaises(ValueError):
            create_random_ending({"reason": None, "probability": 0.5})

        with self.assertRaises(ValueError):
            create_random_ending({"reason": "", "probability": 0.5})

        with self.assertRaises(ValueError):
            create_random_ending({"reason": "Good", "probability": None})

        with self.assertRaises(ValueError):
            create_random_ending({"reason": "Good", "probability": "Bad"})


class TestTimeBasedEnding(unittest.TestCase):
    """Tests TimeBasedEnding"""

    def test_time_based_ending_evaluate(self) -> None:
        """Tests TimeBasedEnding.evaluate()"""
        test_location = Location(name="TEST", description="Test location")

        ending = TimeBasedEnding(reason="Test", turn_limit=23)

        no_trigger = State(turn_no=22, location=test_location)
        self.assertFalse(ending.evaluate(no_trigger))

        trigger = State(turn_no=23, location=test_location)
        self.assertTrue(ending.evaluate(trigger))

        also_trigger = State(turn_no=24, location=test_location)
        self.assertTrue(ending.evaluate(also_trigger))

    def test_create_time_based_ending_valid(self) -> None:
        """Tests create_time_based_ending() with valid data"""
        ending = create_time_based_ending({"reason": "Reason", "turn_limit": 1337})
        self.assertIsInstance(ending, TimeBasedEnding)
        self.assertEqual(ending.reason, "Reason")
        self.assertEqual(ending.turn_limit, 1337)

    def test_create_time_based_ending_invalid(self) -> None:
        """Tests create_time_based_ending() with invalid data"""
        with self.assertRaises(ValueError):
            create_time_based_ending({})

        with self.assertRaises(ValueError):
            create_time_based_ending({"reason": None, "turn_limit": 1337})

        with self.assertRaises(ValueError):
            create_time_based_ending({"reason": "", "turn_limit": 1337})

        with self.assertRaises(ValueError):
            create_time_based_ending({"reason": "Good", "turn_limit": None})

        with self.assertRaises(ValueError):
            create_time_based_ending({"reason": "Good", "turn_limit": "Bad"})


class TestGoalBasedEnding(unittest.TestCase):
    """Tests GoalBasedEnding."""

    def setUp(self) -> None:
        self.location_ab = Location(name="AB", description="AB")
        self.location_abc = Location(name="ABC", description="ABC")
        self.location_xyz = Location(name="XYZ", description="XYZ")

        item_a = Item(name="A", description="A", takeable=True)
        item_b = Item(name="B", description="B", takeable=True)
        item_c = Item(name="C", description="C", takeable=True)
        item_x = Item(name="X", description="X", takeable=True)
        item_y = Item(name="Y", description="Y", takeable=True)
        item_z = Item(name="Z", description="Z", takeable=True)

        self.items_a = ItemContainer(contents=[item_a])
        self.items_ab = ItemContainer(contents=[item_a, item_b])
        self.items_abc = ItemContainer(contents=[item_a, item_b, item_c])
        self.items_xyz = ItemContainer(contents=[item_x, item_y, item_z])

        self.state_ab = State(
            turn_no=1, location=self.location_ab, inventory=self.items_ab
        )
        self.state_abc = State(
            turn_no=1, location=self.location_abc, inventory=self.items_abc
        )
        self.state_xyz = State(
            turn_no=1, location=self.location_xyz, inventory=self.items_xyz
        )

        self.world = World(contents=self.items_abc.contents + [self.location_abc])

    def test_goal_based_ending_evaluate_empty(self) -> None:
        """Tests GoalBasedEnding.evaluate() with neither items nor location"""
        empty_ending = GoalBasedEnding(reason="Test")
        self.assertTrue(empty_ending.evaluate(self.state_ab))
        self.assertTrue(empty_ending.evaluate(self.state_abc))
        self.assertTrue(empty_ending.evaluate(self.state_xyz))

    def test_goal_based_ending_evaluate_items(self) -> None:
        """Tests GoalBasedEnding.evaluate() with items"""
        one_item_ending = GoalBasedEnding(reason="Test", items=self.items_a)
        self.assertTrue(one_item_ending.evaluate(self.state_ab))
        self.assertTrue(one_item_ending.evaluate(self.state_abc))
        self.assertFalse(one_item_ending.evaluate(self.state_xyz))

        two_items_ending = GoalBasedEnding(reason="Test", items=self.items_ab)
        self.assertTrue(two_items_ending.evaluate(self.state_ab))
        self.assertTrue(two_items_ending.evaluate(self.state_abc))
        self.assertFalse(two_items_ending.evaluate(self.state_xyz))

    def test_goal_based_ending_evaluate_location(self) -> None:
        """Tests GoalBasedEnding.evaluate() with location"""
        ending = GoalBasedEnding(reason="Test", location=self.location_ab)
        self.assertTrue(ending.evaluate(self.state_ab))
        self.assertFalse(ending.evaluate(self.state_abc))
        self.assertFalse(ending.evaluate(self.state_xyz))

    def test_goal_based_ending_evaluate_location_items(self) -> None:
        """Tests GoalBasedEnding.evaluate() with location and items"""
        ending = GoalBasedEnding(
            reason="Test", location=self.location_abc, items=self.items_a
        )
        self.assertFalse(ending.evaluate(self.state_ab))
        self.assertTrue(ending.evaluate(self.state_abc))
        self.assertFalse(ending.evaluate(self.state_xyz))

    def test_create_goal_based_ending_valid(self) -> None:
        """Tests create_goal_based_ending() with valid data"""
        ending_full_data = {
            "reason": "Full",
            "location": "ABC",
            "items": ["A", "B", "C"],
        }

        ending_full = create_goal_based_ending(ending_full_data, self.world)
        self.assertIsInstance(ending_full, GoalBasedEnding)
        self.assertEqual(ending_full.reason, "Full")
        self.assertIs(ending_full.location, self.location_abc)
        self.assertCountEqual(ending_full.items.contents, self.items_abc.contents)

        ending_empty_data = {"reason": "Empty"}
        ending_empty = create_goal_based_ending(ending_empty_data, self.world)
        self.assertIsInstance(ending_empty, GoalBasedEnding)
        self.assertEqual(ending_empty.reason, "Empty")
        self.assertIs(ending_empty.location, None)
        self.assertCountEqual(ending_empty.items.contents, [])

    def test_create_goal_based_ending_invalid(self) -> None:
        """Tests create_goal_based_ending() with invalid data"""

        with self.assertRaises(ValueError):
            create_goal_based_ending({}, self.world)

        with self.assertRaises(ValueError):
            create_goal_based_ending({"reason": None}, self.world)

        with self.assertRaises(ValueError):
            create_time_based_ending({"reason": ""})


if __name__ == "__main__":
    unittest.main()
