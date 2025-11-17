"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Clayan Ariaga

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA DEFINITIONS (Used for creating default files)
# ============================================================================

# Define default quest data blocks
DEFAULT_QUESTS = [
    """QUEST_ID: tutorial_1
TITLE: The First Step
DESCRIPTION: Defeat a single goblin to prove your worth.
REWARD_XP: 100
REWARD_GOLD: 50
REQUIRED_LEVEL: 1
PREREQUISITE: NONE""",
    """QUEST_ID: warrior_path
TITLE: The Orc Menace
DESCRIPTION: Clear the southern woods of a fearsome Orc.
REWARD_XP: 300
REWARD_GOLD: 150
REQUIRED_LEVEL: 3
PREREQUISITE: tutorial_1""",
    """QUEST_ID: mountain_trial
TITLE: The Dragon's Roar
DESCRIPTION: Face the ultimate foe, a Dragon, atop the mountain.
REWARD_XP: 1000
REWARD_GOLD: 500
REQUIRED_LEVEL: 6
PREREQUISITE: warrior_path"""
]

# Define default item data blocks
DEFAULT_ITEMS = [
    """ITEM_ID: health_potion
NAME: Health Potion
TYPE: consumable
EFFECT: health:30
DESCRIPTION: Restores 30 Health.""",
    """ITEM_ID: mana_potion
NAME: Mana Potion
TYPE: consumable
EFFECT: magic:15
DESCRIPTION: Restores 15 Magic (for future use).""",
    """ITEM_ID: rusty_sword
NAME: Rusty Sword
TYPE: weapon
EFFECT: strength:5
DESCRIPTION: A weak but reliable weapon.""",
    """ITEM_ID: leather_armor
NAME: Leather Armor
TYPE: armor
EFFECT: max_health:10
DESCRIPTION: Provides minor defense.""",
]

# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

def _parse_data_block(lines, data_type, required_fields):
    """Internal helper to parse a generic data block."""
    data = {}
    try:
        for line in lines:
            if not line.strip(): continue
            key, value = line.split(": ", 1)
            data[key.strip()] = value.strip()
            
        for field in required_fields:
            if field not in data:
                raise InvalidDataFormatError(f"Missing required field '{field}' in {data_type} block.")
                
        # Type conversion
        if 'REWARD_XP' in data: data['REWARD_XP'] = int(data['REWARD_XP'])
        if 'REWARD_GOLD' in data: data['REWARD_GOLD'] = int(data['REWARD_GOLD'])
        if 'REQUIRED_LEVEL' in data: data['REQUIRED_LEVEL'] = int(data['REQUIRED_LEVEL'])
            
    except ValueError as e:
        raise InvalidDataFormatError(f"Type conversion error in {data_type} block: {e}")
    except Exception as e:
        raise InvalidDataFormatError(f"General parsing error in {data_type} block: {e}")
        
    return data

def parse_quest_block(lines):
    """Parse a block of lines into a quest dictionary."""
    required = ['QUEST_ID', 'TITLE', 'DESCRIPTION', 'REWARD_XP', 'REWARD_GOLD', 'REQUIRED_LEVEL', 'PREREQUISITE']
    return _parse_data_block(lines, "quest", required)

def parse_item_block(lines):
    """Parse a block of lines into an item dictionary."""
    required = ['ITEM_ID', 'NAME', 'TYPE', 'EFFECT', 'DESCRIPTION']
    return _parse_data_block(lines, "item", required)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def _load_data_file(filename, parse_func, id_key):
    """Internal helper to load and parse a generic data file."""
    data_dict = {}
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"Data file not found: {filename}")
    except Exception as e:
        raise CorruptedDataError(f"Error reading file {filename}: {e}")

    # Split content into blocks by two or more newlines
    blocks = [b.strip().split('\n') for b in content.split('\n\n') if b.strip()]

    for block in blocks:
        if not block: continue
        try:
            parsed_data = parse_func(block)
            data_id = parsed_data[id_key]
            if data_id in data_dict:
                raise InvalidDataFormatError(f"Duplicate ID found: {data_id} in {filename}")
            data_dict[data_id] = parsed_data
        except InvalidDataFormatError as e:
            raise InvalidDataFormatError(f"Error in {filename} block: {e}")
            
    return data_dict

def load_quests(filename="data/quests.txt"):
    """Load quest data from file."""
    return _load_data_file(filename, parse_quest_block, 'QUEST_ID')

def load_items(filename="data/items.txt"):
    """Load item data from file."""
    return _load_data_file(filename, parse_item_block, 'ITEM_ID')

# ============================================================================
# DATA FILE CREATION
# ============================================================================

def create_default_data_files():
    """
    Create the 'data' directory and default quest/item files if they don't exist.
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # Write Quests
    quest_file = os.path.join(data_dir, "quests.txt")
    if not os.path.exists(quest_file):
        with open(quest_file, 'w') as f:
            f.write('\n\n'.join(DEFAULT_QUESTS))
            
    # Write Items
    item_file = os.path.join(data_dir, "items.txt")
    if not os.path.exists(item_file):
        with open(item_file, 'w') as f:
            f.write('\n\n'.join(DEFAULT_ITEMS))
            
    print("Default data files created in the 'data/' directory.")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    create_default_data_files()
    
    # Test loading quests
    try:
        quests = load_quests()
        print(f"Loaded {len(quests)} quests:")
        for q_id, q_data in quests.items():
            print(f" - {q_data['TITLE']} (Lvl {q_data['REQUIRED_LEVEL']})")
    except MissingDataFileError:
        print("Quest file not found (should not happen after creation)")
    except InvalidDataFormatError as e:
        print(f"Invalid quest format: {e}")
    except CorruptedDataError as e:
        print(f"Corrupted quest file: {e}")
    
    # Test loading items
    try:
        items = load_items()
        print(f"Loaded {len(items)} items:")
        for i_id, i_data in items.items():
            print(f" - {i_data['NAME']} ({i_data['TYPE']})")
    except MissingDataFileError:
        print("Item file not found (should not happen after creation)")
    except InvalidDataFormatError as e:
        print(f"Invalid item format: {e}")
    except CorruptedDataError as e:
        print(f"Corrupted item file: {e}")
