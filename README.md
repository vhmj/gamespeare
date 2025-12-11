# Gamespeare - An Adventure Game Engine
Gamespeare is a game engine for adventure games. Currently, text adventure games
are supported.

## Requirements

Python version 3.10 is required to run the game engine. No other dependencies
are required.

## Playing a Game
Using the game engine requires executing  `__main__.py` one way or another
from a console capable of text input and output.

Simply executing ```python gamespeare``` will show basic usage information:

```
usage: python gamespeare [-h] filename
```

Executing ```python gamespeare -h``` will show extended usage information:

```
Gamespeare - A Text Adventure Game Engine

positional arguments:
  filename              path of game to play

options:
  -h, --help            show this help message and exit
```

Finally, executing the engine with the path to a JSON game file as a parameter
will start the game.

```python gamespeare data/demo.json```

```
You are Hamlet, prince of Denmark.

Gertrude's birthday is coming up, but you can not find the beautiful kamelåså
you had the finest smiths in all of Denmark make for her.

Where can it be?

Turn #1: ROOM

A room in the castle. Pretty cozy.

You can see the following items here:
CHEST: A sturdy chest

You can see the following exits:
NORTH

You have the following items:
SWORD: A sharp sword

What do you want to do? (HELP for help)
> 
```

After this, playing the game should be straightforward. Enter one command and
press enter to se what happens:

```
What do you want to do? (HELP for help)
> HELP

Valid Commands in the Turn of Our Lord 1:

GO [direction]
    Example: GO NORTH
USE [item] ON [other item]
    Example: USE KEY ON CHEST
TAKE [item]
    Example: TAKE SKULL
HELP
    Example: HELP
QUIT
    Example: QUIT

What do you want to do? (HELP for help)
>
```

## Running the Unit Tests
Unit tests are located in the `test` module, with supporting data files located
in the folder `testdata`.

The unit test can be executed using ```python -m unittest```

## Game Engine Structure
An `AdventureGame` is initialized with a `Playbook` containing the `Story`
to be experienced, from `prologue` to `epilogue` via a triggered `Ending`. The
`Playbook` also contains the `World` the game takes place in, made up of at
least one `Location`, and optionally one `Item` or more. Additionally, the
`Playbook` keeps track of the current `State` of the game, with the current
`turn_no`, the player's current `location` and `inventory` of `Item`s. 

The game is started by calling `play()`, which initiates a looped sequence of...

1. `Action` selection
2. `Action` execution
3. Presentation of consequences of `Action` execution

...until the player quits or an `Ending` is triggered.

The `AdventureGame` is an I/O agnostic abstract implementation of the game
engine. In order to have a playable game engine, certain methods must be
implemented, responsible for presenting the `Story`, `World` and current `State`
to the user, and to select an `Action` every turn as well as to present the
consequences of the `Action` as provided by `AdventureGame`.

Currently, `TextAdventureGame`, is the available playable implementation. It
uses the console for text input and text output.




### Game Data File Format

The game data file format is a JSON file, simplified below. See the file
`data/demo.json` for an authentic example.

```
{
  "world": {
    "items": list[Item]
    "locations": list[Location]
  },
  "story": {
    "prologue": str,
    "epilogue": str,
    "endings": list[Ending]
  },
  "state": {
    "turn_no": int,
    "location": str,
    "inventory": list[str]
  }
}
```

#### Item
There are currently two types of items, regular items (`ITEM`) and containers
(`CONTAINER`). Each item must have a unique uppercase name. Items are optional.

```
{
  "class": "ITEM",
  "name": "SKULL",
  "description": "Yorick's skull"
},
{
  "class": "CONTAINER",
  "name": "CHEST",
  "description": "A sturdy chest",
  "key": "KEY",
  "contents": [
    "SKULL", "POISON"
  ]
}
```

#### Location
Each location (`LOCATION`) must have a unique uppercase name. Every location can
contain optional items, identified by their unique names, as well as optional
destinations. Destinations are specified by key-value pairs, where the key is
the uppercase direction, and the value the destination, identified by its unique
name.

```
  {
    "class": "LOCATION",
    "name": "COURTYARD",
    "description": "The courtyard. Scary. There is a big hole in the ground.",
    "items": [
      "KEY",
      "SKULL",
      "STATUE"
    ],
    "destinations": {
      "INSIDE": "HALL",
      "DOWN": "HOLE"
    }
```

#### Ending
There are currently three classes of endings. The first `Ending` is a time-based
ending, ending the game after a specified number of turns:

```
{
  "class": "TURNS",
  "reason": "Oh no! Time's up!",
  "turn_limit": 20
}
```

The second `Ending` is goal-based, and triggers when the `State` matches both
the  optional `location` and all specified items (if any) are part of the
`ìnventory`.

```
{
  "class": "GOAL",
  "reason": "Great job! You completed the mission! Time to eat!",
  "location": "DINING ROOM"
  "items": [
    "FORK", "KNIFE", "PLATE", "SPOON"
  ]
}
```

The third `Ending` is random, based on a probability in the range [0.0, 1.0].

```
{
  "class": "RANDOM",
  "reason": "Oh no! Hamlet suffered a stroke!",
  "probability": 0.01
}
```
