## Introduction

This (as-yet nameless) library was created as a five-day, part-time work sample at the request of hiring manager TA. It allows a programmer (the "user" or "game designer") to implement rudimentary old-school text adventures, which are playable at a computer terminal.

To play the example game, "Bread Master", download this repository and run `python3 breadmaster.py`.

### Aims

**Guiding principles for this project.**

1. Hit the mark.

    TA gave me free reign to submit any code sample I chose. Having developed interactive fiction but never made my own tool for such, I set out to build a small but complete text-adventure engine. I defined "complete" to mean I could hand the library to another programmer and expect them to be able to make a game, ideally after no more introduction than reading and playing the sample game, "Bread Master" (see `breadmaster.py`.)
    
2. Do right by both the user and the user's user, the game player.

    I wanted the user to be able to open this library, read the thirty or forty lines of code that specify "Bread Master", play that game, and be ready to write his own little game. [**For explicit user instructions, see "Instructions for Game Designers" below**.]
    
    It seemed to me that, if I were a game designer thinking about using this game library, the most important thing would be an assurance that my players would be well-served out of the box. Thus, I tried to include quality-of-life features for players of games made with this library, including a help menu listing commands and their synonyms; parser special cases to allow more freedom in typing `Command`s; and prompting the player with choices of direct object if they failed to provide one for a targetable `Command`, rather than rejecting their command outright.
    
3. Document design decisions.

    Having been a research programmer, I believe a long-term software project is most likely to succeed if one can make progress on it even if only able to return to it at intermittent intervals. The way to achieve that state is to ensure that the code is no trickier than it needs to be, and that any potential sources of confusion are patiently explained, in as much English as is necessary.
    
    My standard of achievement for Aim 3 was that, anywhere Future Me or Future You might have been confused or skeptical, that emotion would be dispelled in code commentary or this README. I couldn't achieve lofty heights in five days, but I could make crystal-clear the reasons behind my choices and the next steps for continued work.

4. Convince TA I'm the right man for the job.

    The role for which TA is considering me is a bit unusual. The team is small, and the work isn't tied to the quarterly business cycle. I'd be assisting TA with long-term, grant-funded research by improving an existing codebase. While assisting with new features would be part of the job, the primary duties would be refactoring, testing, and above all **thinking**. In this repository, I hope I've shown that I can think long-term, keep track of what needs doing and what's unimportant, justify my design choices, write clean code, explain my code to others, and put user needs first.

### Features

A library user can:

- implement custom `Item`s (including `Room`s) with synonyms
- choose the player's starting `Room` and inventory `Item`s
- set an introductory message for the game
- set the game's win conditions
- set a win message for the game
- define custom functions for activatable `Item`s, which change game-world state or give `Item`s additional functionality

Game players enjoy engine convenience features such as:

- typing multiple commands at one time (if you enter "go north. take jelly", the engine will run "go north" and "take jelly" in sequence)
- being prompted to enter the "help" command if your command is unrecognized
- command synonyms (example: "pick up", "take", "get" are all interpreted as the "take" command)
- parseable articles (example: "take the doll", "take a doll", "take teh doll" are all interpreted as "take doll")
- being prompted for a direct object when you forget one (example: if you just enter "take", the engine will prompt you to choose a currently-visible object)

### Scope

Many possible features were out of scope given time and quality constraints. In general, if I felt I wanted to add something but wouldn't be able to do so without failing to achieve Aim 1, I erred on the side of documenting it in this README to show that I'd at least considered the problem. This prevented me from dancing to the seductive song of scope creep. Things I left out include:

- ability for user to implement custom `Command`s
- the possibility of losing the game or displaying a losing message
- scoring or other measurement (other than `win_function`)
- turn count and/or timed actions
- NPCs
- stateful `Item`s
- many typical adventure-game commands (notably, "take" is implemented but counterpart "drop" is not)

## Instructions for Game Designers

*For an example file which shows all these steps, see `breadmaster.py` in this repository.*

1. In a Python file, import everything from `runner.py`.
2. In a string variable, write a sentence or two which situates your player in the game, and introduces the identity of their player character. This will be printed when the game starts. You might consider including the game's title, author, and other publication info within this string.
3. Define any custom functions you need for your game. At minimum, you will need to define a win condition (see `runner.GameRunner` and the "Bread Master" example for more info.) If you want items to have custom effects, you can define functions to pass in for their `activate_fn` parameter; this allows you to change game state in response to player commands, or provide different options for activating an `Item` based on the current game state.
4. Define the `Item`s your player will be able to interact with in your game. Each one needs a name, a description, and a list of the commands to which it can respond (aside from "look", which is always available.)
5. Define the `Room`s which constitute the game world's structure. Each one needs a name, a description, a dictionary mapping from Directions to other room names, and a list of the items which populate that room at the beginning of the game.
6. Write a message to show the player when they win your game.
7. Define the Items, if any, which the player will have on their person when the game begins.
8. In your `main()` function, pass all of the above to the `GameRunner` constructor, then ensure `main()` is called when your Python file is run.
9. Test out your game!

## Directions for Further Work

### Potential Extensions

**New features which could be added to enhance the user or player experience.**

- Partially/totally restructure `game_loop` as an explicit state machine
    
    With the library having acquired a definite structure, it's clear that most of the complexity occurs in responding to player input within `game_loop`. The library reads input, passes the input through transformations and validations, and then declares the input invalid (with a message to the player), partially valid (with a request for more info from the player), or valid (with action taken to carry out the necessary update to the game state.)

    [There's also "quit", which is valid input but not an actual Command.]
   
    Since partially-valid inputs trigger further player data entry, all inputs are eventually judged valid or invalid. This sequence of "read input -> perform actions on input -> (eventually) accept or reject" can be modeled as a state machine.

    Right now that state machine is implied by the structure of the if-else tree in `game_loop`. Explicitly modeling this machine with a function for handling each step of the decision process would improve `game_loop` readability, and make it possible for a game designer to extend the library with new Commands by adding new functions to the representation of the state machine.

- Allow game designer to automatically test their game by feeding `GameRunner` a list of commands to use as simulated player actions
    
- Support multi-word names for `Item` and `Room`

    At minimum, this would require changes to `GameRunner.parse_object` and to how synonyms are canonicalized (checked to see if they refer to an `Item.name`.)

- Make commands extensible within user code rather than having to edit `commands.COMMANDS`

    I don't have a plan for this right now, but it's a necessity in serious game-creation libraries of this type.

### Shortcomings

**Known issues which will be addressed should I seriously continue development.**

- Improve library use of validation and testing

    I've taken some pains to respond to malformed or erroneous player commands with an informative message, and I've tried catching a number of possible errors by the game designer (usually in class constructors). The library still could use additional safeguards against errors by the game designer.
    
    Sample approaches:
    
    - Add Python type hinting to run the library through MyPy, helping to catch problems like a malformed `Room.exits`.
    
    - Add unit tests for `helpers` functions.
    
    See also "automated testing", above.

- Possible `Item` names are shadowed by special cases for parsing Commands and direct objects 

    The current rudimentary implementation of `parse_objects` mercilessly strips "a", "the", "an" and a few other "dummy words" to provide a better interface for the player -- but this restricts the user's ability to program in an `Item` named, say, "AN" (audio novel?). It's OK to restrict the user in that way, but I am then responsible for adding code which enforces that restriction. [These concerns also apply to the special case which allows the player to type "look around", "look surroundings", etc. and get back the results of looking at `current_room`.]
    
    To fix: either (1) make the tokenizer and/or parsing code smarter or (2) register all "special" words somewhere, then add validation for `Item` names which brute-force disallows those from being used in/as `Item` names.

- Certain `GameRunner.flags` keys are used internally, so game designer should be prevented from setting those keys

    This is similiar to the previous issue, where potential `Item` and `Room` names are no-gos because they conflict with parsing special cases. Certain keys in the `flags` dict are used by the library itself: for example, the game loop checks the "multi" key to decide whether to execute previously-entered commands. The game designer should therefore be prevented from setting those keys.
    
    In the `Item`/`Room` case, we can check when calling `GameRunner.__init__` that no reserved names are used. In the case of `flags` keys, though, we have no way of knowing in advance which ones the user might set inside, say, custom Item-activation functions.
    
    One solution would be to re-implement `flags` as a wrapped dict, using `collections.abc` or similar, which behaves as a normal dict except that it raises a `GameError` if the user tries to set the reserved keys. This will cause the issue to reveal itself to the game designer when they test their game (and if they don't, well, that's their problem.)
    
- Overuse of strings to represent data-that-means-exactly-itself

    This stems from Python lacking a proper 'evaluates-to-itself' data type, unlike Lisp/Ruby keywords, Lisp quoted symbols, or algebraic data types. Strings are the primary option. You can get pretty far with string-keyed dictionaries and occasional use of `instance.hasattr(a_string)`, but strings present two major problems that keywords or ADTs avoid:
    
    1. The user is given the opportunity to screw up by making typos, which are hard to debug or even notice until they cause runtime errors.
    2. Strings do not represent exactly one thing: the same string might well be reused twice in two parts of a program with different meaning.
    
    My understanding is that Python 3.6's Dataclass module was invented to fill this void. If I continued development, I'd find ways to employ it. (The requirement for 3.6 would also license use of f-strings: see "clunky formatting.")

- Target `Item` parsing needs more abstraction

    Right now, target parsing & validation for commands that require a target, like "look" and "take", is somewhat repetitive. This repetition ought to be substantially reduced, in keeping with DRY.
    
    A good starting point would be to move more target-parsing code into `parse_object`.
    
### Apparent Shortcomings Which I Say Aren't

**Design decisions which might otherwise look like missteps.**

- All state is stored in `GameRunner` attributes, rather than devolving any to `Item` instances

    I'd improve game-state management if I were to keep working on this library. In a complicated game, `GameRunner.flags` threatens to accumulate so much state that every decision in the command-handling portion of `GameRunner.game_loop` becomes a thicket of reasoning. Furthermore, it'd be a pain to implement stateful `Item`s (e.g. a machine that stays turned on until it's switched off) right now, and users have no way to hack that in.

    However, I think the choice is defensible given I wrote this as a prototype under time pressure. For text-adventure games -- really, games in general -- logic which requires reasoning about the state of multiple objects always crops up sooner or later. This library is small, as are the games you'd want to build with it. I'd rather centralize game state within `GameRunner` so that all the statefulness can be understood from one location, rather than having it scattered among the attributes of many `Item`s.

- One-way `Room` connections are allowed, e.g. room A goes south to room B without making a connection from B to A

    This is by design. It should be possible to represent a slippery slide that brings you from A to B, but cannot be climbed up to go the other way. [If I wanted to prevent this, I'd add validation, in the `GameRunner` constructor, of the connections defined in `self.rooms`.]
    
    Note that `Room` constructor **does** raise an error if it is given no exits.
    
- Clunky string formatting

    I wasn't asked to write against a particular version of Python 3, so to ensure compatibility with versions before 3.6, I avoided using f-strings in favor of `string.format()`, `string.join()`, and good old concatenation. Given the string- and printing-heavy nature of an adventure game library, if I continued working on this, I'd require 3.6 and use f-strings. However, I don't think there's anything wrong with the "old-fashioned" approach.

- Checking membership in lists

    Testing `if X in Y` where `Y` is a list is linear in the length of the list. So far, I've avoided coding list-membership tests in favor of set-membership tests, except in cases where the lists are small, and not exposed to the game designer (e.g. runner.py, line 169 `if target in ["player"...]`).
    
    However, in a game which places a lot of `Item`s in a single `Room` or allows/compels the player to pick up lots of `Item`, runner.py, line 171, `elif maybe_item in self.current_room.items + self.inventory` could take a long time to run.
    
    Without a test case showing that this membership test requires so long to run that it has a perceptible negative effect on player experience, there's no need to change the code. It's merely worth noting here in case this library gets used to make large-scale games.

- Popping the heads of lists

    There are some instances where the code calls `list.pop(0)`. I'm aware that in Python, the best performance is had by appending and popping at the end of a list. I will change whatever needs to be changed if a performance issue arises.
