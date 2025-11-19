# COMP 163: Project 3 - Quest Chronicles
**Student Name:** Clayan Ariaga  
**Date:** November 18, 2025  
**AI Usage Policy:** Free Use (with explanation requirement)

---

## Project Overview

Quest Chronicles is a text-based RPG adventure game built using Python's modular design principles. The game demonstrates mastery of **exceptions** and **modules** by organizing functionality into seven interconnected modules, each with specific responsibilities and proper error handling.

Players create characters, accept quests, battle enemies, manage inventory, and level up through a complete RPG experience—all from the command line.

---

## Module Architecture

### 1. **custom_exceptions.py** (PROVIDED)
- **Purpose:** Defines all custom exception classes used throughout the game
- **Key Exceptions:**
  - `GameError` - Base exception for all game errors
  - `CharacterError`, `QuestError`, `InventoryError`, `CombatError`, `DataError` - Specific error categories
- **Dependencies:** None (imported by all other modules)

### 2. **game_data.py** 
- **Purpose:** Handles loading and validating game data from text files
- **Key Functions:**
  - `load_quests()` - Parses `data/quests.txt` into dictionary
  - `load_items()` - Parses `data/items.txt` into dictionary
  - `validate_quest_data()` / `validate_item_data()` - Ensures data integrity
- **Dependencies:** Imports `custom_exceptions`
- **Data Format:** Text files with key-value pairs separated by double newlines

### 3. **character_manager.py** 
- **Purpose:** Manages character creation, persistence, and stat operations
- **Key Functions:**
  - `create_character()` - Creates character with class-specific stats
  - `save_character()` / `load_character()` - File I/O for persistence
  - `gain_experience()` - Handles XP and automatic level-ups
  - `add_gold()` / `heal_character()` - Resource management
- **Dependencies:** Imports `custom_exceptions`
- **Design Choice:** Stores characters as dictionaries for easy serialization to text files

### 4. **inventory_system.py** 
- **Purpose:** Handles item management, equipment, and shop transactions
- **Key Functions:**
  - `add_item_to_inventory()` / `remove_item_from_inventory()` - Basic inventory operations
  - `equip_weapon()` / `equip_armor()` - Equipment with stat bonuses
  - `use_item()` - Consumable item effects
  - `purchase_item()` / `sell_item()` - Shop functionality
- **Dependencies:** Imports `custom_exceptions` and `character_manager` (for gold/healing)
- **Design Choice:** Equipped items stored as `item_id` strings (not full dicts) to keep save files simple

### 5. **quest_handler.py** 
- **Purpose:** Manages quest acceptance, completion, and prerequisite chains
- **Key Functions:**
  - `accept_quest()` - Validates level, prerequisites, completion status
  - `complete_quest()` - Grants rewards via `character_manager`
  - `get_available_quests()` - Filters quests player can accept
  - `validate_quest_prerequisites()` - Ensures no circular dependencies
- **Dependencies:** Imports `custom_exceptions` and `character_manager` (for rewards)
- **Design Choice:** Prerequisite system allows linear quest chains (e.g., quest2 requires quest1)

### 6. **combat_system.py** 
- **Purpose:** Implements turn-based combat with class-specific abilities
- **Key Components:**
  - `create_enemy()` - Factory function for goblin/orc/dragon
  - `SimpleBattle` class - Manages combat loop, turn order, cooldowns
  - `use_special_ability()` - Class-specific abilities (Warrior: Power Strike, Mage: Fireball, etc.)
- **Dependencies:** Imports `custom_exceptions` and `character_manager` (for death checks, healing)
- **Design Choice:** SimpleBattle is a class (not just functions) to maintain combat state (turn count, cooldowns)

### 7. **main.py** (130 lines)
- **Purpose:** Game launcher that orchestrates all modules
- **Key Functions:**
  - `main_menu()` / `new_game()` / `load_game()` - Entry points
  - `game_loop()` - Main gameplay loop with auto-save
  - `view_stats()` / `view_inventory()` / `quest_menu()` / `explore()` / `shop()` - Feature menus
- **Dependencies:** Imports ALL other modules
- **Design Choice:** Uses global variables (`current_character`, `all_quests`, `all_items`) for game state

### Module Dependency Diagram
```
custom_exceptions.py  (base - no dependencies)
        ↑
        ├── game_data.py
        ├── character_manager.py
        ├── inventory_system.py  ← uses character_manager
        ├── quest_handler.py     ← uses character_manager
        ├── combat_system.py     ← uses character_manager
        └── main.py              ← uses ALL modules
```

---

## Exception Handling Strategy

### Philosophy
Exceptions are raised **at the point of error** and caught **at the user interaction level** (in `main.py`). This separates error detection from error handling.

### Key Exception Examples

#### 1. **InvalidCharacterClassError**
- **When:** User selects invalid class during character creation
- **Where Raised:** `character_manager.create_character()`
- **Where Caught:** `main.py` → `new_game()`
- **Why:** Validates input before creating character object

#### 2. **InventoryFullError**
- **When:** Trying to add item when inventory has 20/20 items
- **Where Raised:** `inventory_system.add_item_to_inventory()`
- **Where Caught:** `main.py` → `shop()` or `view_inventory()`
- **Why:** Prevents inventory overflow, forces player decisions

#### 3. **QuestRequirementsNotMetError**
- **When:** Accepting quest without completing prerequisite
- **Where Raised:** `quest_handler.accept_quest()`
- **Where Caught:** `main.py` → `quest_menu()`
- **Why:** Enforces quest progression order

#### 4. **CharacterDeadError**
- **When:** Attempting actions (gain XP, start battle) while health ≤ 0
- **Where Raised:** `character_manager.gain_experience()`, `combat_system.SimpleBattle.start_battle()`
- **Where Caught:** `main.py` → `game_loop()` (triggers revive prompt)
- **Why:** Prevents game-breaking actions while dead

#### 5. **MissingDataFileError**
- **When:** `quests.txt` or `items.txt` not found
- **Where Raised:** `game_data.load_quests()` / `load_items()`
- **Where Caught:** `main.py` → `load_game_data()` (triggers `create_default_data_files()`)
- **Why:** Graceful fallback to default content

### Exception Hierarchy
```
GameError (base)
├── DataError
│   ├── InvalidDataFormatError
│   ├── MissingDataFileError
│   └── CorruptedDataError
├── CharacterError
│   ├── InvalidCharacterClassError
│   ├── CharacterNotFoundError
│   ├── InsufficientLevelError
│   └── CharacterDeadError
├── InventoryError
│   ├── InventoryFullError
│   ├── ItemNotFoundError
│   ├── InsufficientResourcesError
│   └── InvalidItemTypeError
├── QuestError
│   ├── QuestNotFoundError
│   ├── QuestRequirementsNotMetError
│   ├── QuestAlreadyCompletedError
│   └── QuestNotActiveError
└── CombatError
    ├── InvalidTargetError
    ├── CombatNotActiveError
    └── AbilityOnCooldownError
```

---

## Major Design Choices

### 1. **Character Storage Format**
- **Decision:** Characters stored as dictionaries, saved to text files with `KEY: VALUE` format
- **Rationale:** 
  - Simple to read/write without external libraries (no JSON/pickle)
  - Human-readable save files (easy debugging)
  - Uses only concepts covered in class (file I/O, string manipulation)
- **Trade-off:** More parsing code vs. simplicity

### 2. **Equipped Items as Strings**
- **Decision:** `character['equipped_weapon']` stores `"iron_sword"` (item_id), not full item dict
- **Rationale:**
  - Avoids data duplication in save files
  - Item stats fetched from `all_items` dict when needed
  - Simpler save/load logic
- **Trade-off:** Requires item dict lookup vs. direct access

### 3. **SimpleBattle Class vs. Functions**
- **Decision:** Combat uses a class (`SimpleBattle`) instead of standalone functions
- **Rationale:**
  - Maintains state (turn count, cooldowns, combat_active flag)
  - Encapsulates combat logic in one object
  - Easier to test and extend
- **Trade-off:** Slightly more complex than pure functions

### 4. **Automatic Level-Up Loop**
- **Decision:** `gain_experience()` automatically applies multiple level-ups if XP ≥ threshold
- **Rationale:**
  - Player could gain 500 XP from quest → should level up 5 times automatically
  - Avoids "stuck" XP that doesn't apply
- **Implementation:** `while character['experience'] >= character['level'] * 100:`

### 5. **Quest Prerequisite Validation**
- **Decision:** Validate entire quest chain at game load (not per-quest)
- **Rationale:**
  - Catches circular dependencies early
  - Prevents broken quest chains from bad data
- **Function:** `validate_quest_prerequisites()` in `quest_handler.py`

---

## AI Usage Disclosure

### AI Tools Used
- **ChatGPT/Claude** - Used for:
  1. Debugging test compatibility issues (equipped items storage format)
  2. Structuring module organization and dependencies
  3. Optimizing code length while maintaining readability
  4. Understanding exception handling patterns

### What AI Helped With
- **Module Structure:** AI suggested organizing exceptions into hierarchy, separating data loading from game logic
- **Bug Fixes:** AI identified that tests expected `equipped_weapon` as string, not dict
- **Code Refactoring:** AI helped reduce code from ~1750 lines to ~720 lines by removing redundancy
- **Error Handling:** AI recommended `raise_exceptions` parameter in `can_accept_quest()` for dual use
- **Constructing README:** AI was used in creating the README and putting everything all togather

### What I Did Myself
- Implemented all game logic and features independently
- Designed stat system and class balance (Warrior/Mage/Rogue/Cleric)
- Created combat formulas and special ability effects
- Wrote all menu systems and user interaction flows
- Debugged and tested all functionality

### Learning Outcomes
Through AI assistance, I learned:
- How to organize large projects into cohesive modules
- Best practices for exception hierarchies
- When to use classes vs. functions (SimpleBattle vs. inventory functions)
- How to write concise, readable code without sacrificing clarity

---

## How to Play

### Installation
1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd quest_chronicles
   ```

2. Ensure you have Python 3.7+ installed:
   ```bash
   python3 --version
   ```

3. Run the game:
   ```bash
   python3 main.py
   ```

### Gameplay Instructions

#### Starting the Game
1. Launch `main.py`
2. Choose **New Game** or **Load Game**
3. For new game:
   - Enter character name (alphanumeric, no spaces)
   - Choose class:
     - **Warrior:** High HP/Strength, Power Strike ability
     - **Mage:** High Magic, Fireball ability
     - **Rogue:** Balanced, Critical Strike ability (50% chance)
     - **Cleric:** Balanced, Heal ability

#### Main Game Loop
From the game menu, you can:
- **View Stats:** See level, HP, XP, equipped items, quest progress
- **Inventory:** Use consumables, equip weapons/armor, manage items
- **Quests:** Accept/abandon quests, view available/active/completed
- **Explore:** Random enemy encounters based on your level
- **Shop:** Buy/sell items (items sell for 50% of purchase price)
- **Save & Quit:** Auto-saves progress and returns to main menu

#### Combat System
- **Turn-based:** You attack, then enemy attacks
- **Options per turn:**
  1. **Attack:** Deal damage based on Strength or Magic
  2. **Special Ability:** Class-specific ability (2-turn cooldown)
  3. **Run:** 50% chance to escape (forfeit rewards)
- **Victory:** Gain XP and gold
- **Defeat:** Triggers death screen (revive for 50 gold or game over)

#### Quest System
- Quests have **level requirements** and **prerequisites**
- Example: Can't accept "Dragon Slayer" until "Orc Menace" is complete
- Completing quests grants XP and gold
- View available quests to see what you can accept

#### Leveling System
- **XP to Level:** `current_level × 100` XP required
- **On Level Up:**
  - Max Health +10
  - Strength +2
  - Magic +2
  - Health restored to full

#### Tips
- Buy health potions before exploring
- Equip weapons/armor to boost stats
- Complete easier quests before harder ones
- Save often (auto-saves after each action)

### Controls
- All inputs are number choices or text entry
- Press `Enter` to continue after messages
- Type quest IDs exactly as shown (e.g., `first_steps`)

---

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_exception_handling.py -v

# Run with detailed output
pytest tests/ -v --tb=short
```

### Test Coverage
- **Module Structure Tests:** Verify all modules/functions exist
- **Exception Handling Tests:** Ensure exceptions raised correctly
- **Integration Tests:** Test module interactions (character creation → save → load → quest → combat)

### Expected Results
All 24+ test cases should pass if implementation is correct.

---

## File Structure
```
quest_chronicles/
├── main.py                     # Game launcher (130 lines)
├── character_manager.py        # Character management (120 lines)
├── inventory_system.py         # Inventory/equipment (100 lines)
├── quest_handler.py            # Quest system (100 lines)
├── combat_system.py            # Battle mechanics (130 lines)
├── game_data.py                # Data loading (140 lines)
├── custom_exceptions.py        # Exception definitions (PROVIDED)
├── data/
│   ├── quests.txt             # Quest definitions
│   ├── items.txt              # Item database
│   └── save_games/            # Player save files (auto-generated)
├── tests/
│   ├── test_module_structure.py
│   ├── test_exception_handling.py
│   └── test_game_integration.py
└── README.md                   # This file
```

**Total Lines of Code:** ~720 lines (excluding provided files and tests)

---

## Future Improvements

Given more time, I would add:
1. **More Enemy Types:** Expand beyond goblin/orc/dragon
2. **Status Effects:** Poison, burn, stun effects in combat
3. **Party System:** Multiple characters fighting together
4. **Difficulty Modes:** Easy/Normal/Hard with scaled enemy stats
5. **Achievement System:** Track player accomplishments
6. **Better Combat AI:** Enemies use abilities strategically

---

## Acknowledgments

- **COMP 163 Course Materials:** Module organization and exception handling concepts
- **AI Assistance:** ChatGPT/Claude for debugging and optimization
- **Python Documentation:** File I/O and string manipulation references

---

## License

This project is submitted as coursework for COMP 163. All rights reserved.
