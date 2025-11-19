"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Clayan

AI Usage: Gemini, was used on this file based on the provided
starter code, README.md, and data files (items.txt, quests.txt).
My logic involved parsing text files, handling potential file I/O
and formatting errors, and structuring the data into dictionaries.

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)


# ============================================================================
# DEFAULT DATA CREATION (MOVED TO TOP)
# ============================================================================

def create_default_data_files():
    """Create default data files if they don't exist"""
    os.makedirs("data", exist_ok=True)

    quests_content = """QUEST_ID: first_steps
TITLE: First Steps
DESCRIPTION: Begin your adventure by defeating your first enemy
REWARD_XP: 50
REWARD_GOLD: 25
REQUIRED_LEVEL: 1
PREREQUISITE: NONE

QUEST_ID: goblin_hunter
TITLE: Goblin Hunter
DESCRIPTION: The village is being terrorized by goblins
REWARD_XP: 100
REWARD_GOLD: 75
REQUIRED_LEVEL: 2
PREREQUISITE: first_steps

QUEST_ID: equipment_upgrade
TITLE: Better Equipment
DESCRIPTION: Visit the shop and purchase your first equipment
REWARD_XP: 75
REWARD_GOLD: 50
REQUIRED_LEVEL: 2
PREREQUISITE: first_steps

QUEST_ID: orc_menace
TITLE: The Orc Menace
DESCRIPTION: Defeat the band of orcs near the forest
REWARD_XP: 200
REWARD_GOLD: 150
REQUIRED_LEVEL: 3
PREREQUISITE: goblin_hunter

QUEST_ID: dragon_slayer
TITLE: Dragon Slayer
DESCRIPTION: Face the fearsome dragon threatening the kingdom
REWARD_XP: 500
REWARD_GOLD: 500
REQUIRED_LEVEL: 6
PREREQUISITE: orc_menace

QUEST_ID: treasure_hunter
TITLE: Treasure Hunter
DESCRIPTION: Collect 5 different items for your collection
REWARD_XP: 150
REWARD_GOLD: 100
REQUIRED_LEVEL: 3
PREREQUISITE: equipment_upgrade

QUEST_ID: master_adventurer
TITLE: Master Adventurer
DESCRIPTION: Reach level 10 to prove yourself as a true adventurer
REWARD_XP: 1000
REWARD_GOLD: 1000
REQUIRED_LEVEL: 10
PREREQUISITE: dragon_slayer
"""

    items_content = """ITEM_ID: health_potion
NAME: Health Potion
TYPE: consumable
EFFECT: health:20
COST: 25
DESCRIPTION: Restores 20 health points

ITEM_ID: super_health_potion
NAME: Super Health Potion
TYPE: consumable
EFFECT: health:50
COST: 75
DESCRIPTION: Restores 50 health points

ITEM_ID: iron_sword
NAME: Iron Sword
TYPE: weapon
EFFECT: strength:5
COST: 100
DESCRIPTION: A sturdy iron sword that increases strength

ITEM_ID: steel_sword
NAME: Steel Sword
TYPE: weapon
EFFECT: strength:10
COST: 250
DESCRIPTION: A masterwork steel sword for experienced warriors

ITEM_ID: fire_staff
NAME: Fire Staff
TYPE: weapon
EFFECT: magic:8
COST: 200
DESCRIPTION: A magical staff imbued with fire magic

ITEM_ID: leather_armor
NAME: Leather Armor
TYPE: armor
EFFECT: max_health:10
COST: 75
DESCRIPTION: Light armor that increases maximum health

ITEM_ID: steel_armor
NAME: Steel Armor
TYPE: armor
EFFECT: max_health:25
COST: 200
DESCRIPTION: Heavy armor providing excellent protection

ITEM_ID: magic_robe
NAME: Magic Robe
TYPE: armor
EFFECT: magic:5
COST: 150
DESCRIPTION: Enchanted robes that enhance magical power

ITEM_ID: strength_elixir
NAME: Strength Elixir
TYPE: consumable
EFFECT: strength:3
COST: 50
DESCRIPTION: Permanently increases strength by 3

ITEM_ID: wisdom_elixir
NAME: Wisdom Elixir
TYPE: consumable
EFFECT: magic:3
COST: 50
DESCRIPTION: Permanently increases magic by 3
"""

    if not os.path.exists("data/quests.txt"):
        with open("data/quests.txt", 'w') as f:
            f.write(quests_content)

    if not os.path.exists("data/items.txt"):
        with open("data/items.txt", 'w') as f:
            f.write(items_content)


# Ensure data files exist when module is imported
if not os.path.exists("data/quests.txt") or not os.path.exists("data/items.txt"):
    create_default_data_files()


# ============================================================================
# DATA LOADING
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """Load quest data from file"""
    if not os.path.exists(filename):
        raise MissingDataFileError(f"File not found: {filename}")

    try:
        with open(filename, 'r') as f:
            content = f.read()

        blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
        quests = {}

        for block in blocks:
            quest = parse_quest_block(block.split('\n'))
            validate_quest_data(quest)
            quests[quest['quest_id']] = quest

        return quests

    except (IOError, ValueError) as e:
        raise CorruptedDataError(f"Failed to load quests: {e}")


def load_items(filename="data/items.txt"):
    """Load item data from file"""
    if not os.path.exists(filename):
        raise MissingDataFileError(f"File not found: {filename}")

    try:
        with open(filename, 'r') as f:
            content = f.read()

        blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
        items = {}

        for block in blocks:
            item = parse_item_block(block.split('\n'))
            validate_item_data(item)
            items[item['item_id']] = item

        return items

    except (IOError, ValueError) as e:
        raise CorruptedDataError(f"Failed to load items: {e}")


# ============================================================================
# PARSING
# ============================================================================

def parse_quest_block(lines):
    """Parse quest block into dictionary"""
    quest = {}

    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError(f"Invalid line: {line}")

        key, value = line.split(": ", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "quest_id":
            quest['quest_id'] = value
        elif key == "title":
            quest['title'] = value
        elif key == "description":
            quest['description'] = value
        elif key == "reward_xp":
            quest['reward_xp'] = int(value)
        elif key == "reward_gold":
            quest['reward_gold'] = int(value)
        elif key == "required_level":
            quest['required_level'] = int(value)
        elif key == "prerequisite":
            quest['prerequisite'] = value

    return quest


def parse_item_block(lines):
    """Parse item block into dictionary"""
    item = {}

    for line in lines:
        if ": " not in line:
            raise InvalidDataFormatError(f"Invalid line: {line}")

        key, value = line.split(": ", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "item_id":
            item['item_id'] = value
        elif key == "name":
            item['name'] = value
        elif key == "type":
            item['type'] = value.lower()
        elif key == "effect":
            item['effect'] = value
        elif key == "cost":
            item['cost'] = int(value)
        elif key == "description":
            item['description'] = value

    return item


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_data(quest):
    """Validate quest dictionary has required fields"""
    required = ['quest_id', 'title', 'description', 'reward_xp',
                'reward_gold', 'required_level', 'prerequisite']

    for field in required:
        if field not in quest:
            raise InvalidDataFormatError(f"Missing field: {field}")

    if not isinstance(quest['reward_xp'], int):
        raise InvalidDataFormatError("reward_xp must be integer")
    if not isinstance(quest['reward_gold'], int):
        raise InvalidDataFormatError("reward_gold must be integer")
    if not isinstance(quest['required_level'], int):
        raise InvalidDataFormatError("required_level must be integer")

    return True


def validate_item_data(item):
    """Validate item dictionary has required fields"""
    required = ['item_id', 'name', 'type', 'effect', 'cost', 'description']
    valid_types = ['weapon', 'armor', 'consumable']

    for field in required:
        if field not in item:
            raise InvalidDataFormatError(f"Missing field: {field}")

    if item['type'] not in valid_types:
        raise InvalidDataFormatError(f"Invalid type: {item['type']}")

    if not isinstance(item['cost'], int):
        raise InvalidDataFormatError("cost must be integer")

    return True
