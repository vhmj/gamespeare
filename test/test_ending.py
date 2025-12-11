"""Module for testing of endings."""

import random
import unittest

from gamespeare.ending import (
    RandomEnding,
    create_random_ending,
    create_time_based_ending,
    TimeBasedEnding,
    GoalBasedEnding,
    create_goal_based_ending,
)
from gamespeare.state import State


class TestRandomEnding(unittest.TestCase):
    """Tests RandomEnding."""

    def setUp(self):
        random.seed(1234)

    def test_random_ending(self):
        """Tests RandomEnding.evaluate() with p=0.4"""
        state = State(turn_no=1, location="TEST", inventory=set())
        ending = RandomEnding(reason="Test", probability=0.4)
        self.assertEqual(True, ending.evaluate(state))
        self.assertEqual(False, ending.evaluate(state))
        self.assertEqual(False, ending.evaluate(state))
        self.assertEqual(True, ending.evaluate(state))
        self.assertEqual(True, ending.evaluate(state))
        self.assertEqual(False, ending.evaluate(state))

    def test_random_ending_always(self):
        """Tests RandomEnding.evaluate() with p=1.0"""
        state = State(turn_no=1, location="TEST", inventory=set())
        ending = RandomEnding(reason="Test", probability=1.0)

        for _ in range(10000):
            self.assertEqual(True, ending.evaluate(state))

    def test_random_ending_never(self):
        """Tests RandomEnding.evaluate() with p=0.0"""
        state = State(turn_no=1, location="TEST", inventory=set())
        ending = RandomEnding(reason="Test", probability=0.0)

        for _ in range(10000):
            self.assertEqual(False, ending.evaluate(state))

    def test_create_random_ending_valid(self):
        """Tests create_random_ending() with valid data"""
        ending = create_random_ending({"reason": "Reason", "probability": 0.1337})
        self.assertIsInstance(ending, RandomEnding)
        self.assertEqual(ending.reason, "Reason")
        self.assertAlmostEqual(ending.probability, 0.1337)

    def test_create_random_ending_invalid(self):
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
    """Tests TimeBasedEnding."""

    def test_time_based_ending_evaluate(self):
        """Tests TimeBasedEnding.evaluate()"""
        ending = TimeBasedEnding(reason="Test", turn_limit=23)

        no_trigger = State(turn_no=22, location="TEST", inventory=set())
        self.assertFalse(ending.evaluate(no_trigger))

        trigger = State(turn_no=23, location="TEST", inventory=set())
        self.assertTrue(ending.evaluate(trigger))

        also_trigger = State(turn_no=24, location="TEST", inventory=set())
        self.assertTrue(ending.evaluate(also_trigger))

    def test_create_time_based_ending_valid(self):
        """Tests create_time_based_ending() with valid data"""
        ending = create_time_based_ending({"reason": "Reason", "turn_limit": 1337})
        self.assertIsInstance(ending, TimeBasedEnding)
        self.assertEqual(ending.reason, "Reason")
        self.assertEqual(ending.turn_limit, 1337)

    def test_create_time_based_ending_invalid(self):
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

    def setUp(self):
        self.state_ab = State(turn_no=1, location="AB", inventory={"A", "B"})
        self.state_abc = State(turn_no=1, location="ABC", inventory={"A", "B", "C"})
        self.state_xyz = State(turn_no=1, location="XYZ", inventory={"X", "Y", "Z"})

    def test_goal_based_ending_evaluate_empty(self):
        """Tests GoalBasedEnding.evaluate() with neither items nor location"""
        empty_ending = GoalBasedEnding(reason="Test")
        self.assertTrue(empty_ending.evaluate(self.state_ab))
        self.assertTrue(empty_ending.evaluate(self.state_abc))
        self.assertTrue(empty_ending.evaluate(self.state_xyz))

    def test_goal_based_ending_evaluate_items(self):
        """Tests GoalBasedEnding.evaluate() with items"""
        one_item_ending = GoalBasedEnding(reason="Test", items={"A"})
        self.assertTrue(one_item_ending.evaluate(self.state_ab))
        self.assertTrue(one_item_ending.evaluate(self.state_abc))
        self.assertFalse(one_item_ending.evaluate(self.state_xyz))

        two_items_ending = GoalBasedEnding(reason="Test", items={"A", "B"})
        self.assertTrue(two_items_ending.evaluate(self.state_ab))
        self.assertTrue(two_items_ending.evaluate(self.state_abc))
        self.assertFalse(two_items_ending.evaluate(self.state_xyz))

    def test_goal_based_ending_evaluate_location(self):
        """Tests GoalBasedEnding.evaluate() with location"""
        ending = GoalBasedEnding(reason="Test", location="AB")
        self.assertTrue(ending.evaluate(self.state_ab))
        self.assertFalse(ending.evaluate(self.state_abc))
        self.assertFalse(ending.evaluate(self.state_xyz))

    def test_goal_based_ending_evaluate_location_items(self):
        """Tests GoalBasedEnding.evaluate() with location and items"""
        ending = GoalBasedEnding(reason="Test", location="ABC", items={"A"})
        self.assertFalse(ending.evaluate(self.state_ab))
        self.assertTrue(ending.evaluate(self.state_abc))
        self.assertFalse(ending.evaluate(self.state_xyz))

    def test_create_goal_based_ending_valid(self):
        """Tests create_goal_based_ending() with valid data"""
        ending_full = create_goal_based_ending(
            {"reason": "Full", "location": "ABC", "items": ["A", "B", "C"]}
        )
        self.assertIsInstance(ending_full, GoalBasedEnding)
        self.assertEqual(ending_full.reason, "Full")
        self.assertEqual(ending_full.location, "ABC")
        self.assertCountEqual(ending_full.items, ["A", "B", "C"])

        ending_empty = create_goal_based_ending({"reason": "Empty"})
        self.assertIsInstance(ending_empty, GoalBasedEnding)
        self.assertEqual(ending_empty.reason, "Empty")
        self.assertEqual(ending_empty.location, "")
        self.assertCountEqual(ending_empty.items, [])

    def test_create_goal_based_ending_invalid(self):
        """Tests create_goal_based_ending() with invalid data"""
        with self.assertRaises(ValueError):
            create_goal_based_ending({})

        with self.assertRaises(ValueError):
            create_goal_based_ending({"reason": None})

        with self.assertRaises(ValueError):
            create_time_based_ending({"reason": ""})


if __name__ == "__main__":
    unittest.main()
