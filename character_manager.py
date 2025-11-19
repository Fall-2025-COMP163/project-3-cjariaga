"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Clayan Ariaga

AI Usage: Google gemini was used in this file based on the provided
starter code and README.md instructions. This involved implementing
character creation logic with different class stats, file I/O for
saving/loading, list/string manipulation for data conversion,
and implementing game logic for leveling, healing, and gold management.

This module handles character creation, loading, and saving.
"""
import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)


# ============================================================================
# CHARACTER MANAGEMENT
# ============================================================================

def create_character(name, character_class):
    """Create a new character with stats based on class"""
    classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15}
    }

    if character_class not in classes:
        raise InvalidCharacterClassError(f"Invalid class '{character_class}'")

    stats = classes[character_class]
    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": [],
        "equipped_weapon": None,
        "equipped_armor": None
    }


def save_character(character, save_directory="data/save_games"):
    """Save character to file"""
    os.makedirs(save_directory, exist_ok=True)
    path = os.path.join(save_directory, f"{character['name']}_save.txt")

    with open(path, 'w') as f:
        f.write(f"NAME: {character['name']}\n")
        f.write(f"CLASS: {character['class']}\n")
        f.write(f"LEVEL: {character['level']}\n")
        f.write(f"HEALTH: {character['health']}\n")
        f.write(f"MAX_HEALTH: {character['max_health']}\n")
        f.write(f"STRENGTH: {character['strength']}\n")
        f.write(f"MAGIC: {character['magic']}\n")
        f.write(f"EXPERIENCE: {character['experience']}\n")
        f.write(f"GOLD: {character['gold']}\n")
        f.write(f"INVENTORY: {','.join(character['inventory'])}\n")
        f.write(f"ACTIVE_QUESTS: {','.join(character['active_quests'])}\n")
        f.write(f"COMPLETED_QUESTS: {','.join(character['completed_quests'])}\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """Load character from save file"""
    path = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(path):
        raise CharacterNotFoundError(f"Save file not found: {character_name}")

    character = {}

    try:
        with open(path, 'r') as f:
            for line in f:
                if ": " not in line:
                    continue

                key, value = line.split(": ", 1)
                key = key.strip().upper()
                value = value.strip()

                if key == "NAME":
                    character['name'] = value
                elif key == "CLASS":
                    character['class'] = value
                elif key == "LEVEL":
                    character['level'] = int(value)
                elif key == "HEALTH":
                    character['health'] = int(value)
                elif key == "MAX_HEALTH":
                    character['max_health'] = int(value)
                elif key == "STRENGTH":
                    character['strength'] = int(value)
                elif key == "MAGIC":
                    character['magic'] = int(value)
                elif key == "EXPERIENCE":
                    character['experience'] = int(value)
                elif key == "GOLD":
                    character['gold'] = int(value)
                elif key == "INVENTORY":
                    character['inventory'] = value.split(',') if value else []
                elif key == "ACTIVE_QUESTS":
                    character['active_quests'] = value.split(',') if value else []
                elif key == "COMPLETED_QUESTS":
                    character['completed_quests'] = value.split(',') if value else []

    except (IOError, ValueError) as e:
        raise SaveFileCorruptedError(f"Corrupted save file: {e}")

    # Add missing fields
    if 'equipped_weapon' not in character:
        character['equipped_weapon'] = None
    if 'equipped_armor' not in character:
        character['equipped_armor'] = None

    validate_character_data(character)
    return character


def list_saved_characters(save_directory="data/save_games"):
    """Get list of all saved character names"""
    if not os.path.exists(save_directory):
        return []

    characters = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            characters.append(filename.replace("_save.txt", ""))
    return characters


def delete_character(character_name, save_directory="data/save_games"):
    """Delete a character's save file"""
    path = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(path):
        raise CharacterNotFoundError(f"No save file: {character_name}")

    os.remove(path)
    return True


# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """Add experience and handle level ups"""
    if is_character_dead(character):
        raise CharacterDeadError("Cannot gain XP while dead")

    character['experience'] += xp_amount

    while character['experience'] >= character['level'] * 100:
        character['experience'] -= character['level'] * 100
        character['level'] += 1
        character['max_health'] += 10
        character['strength'] += 2
        character['magic'] += 2
        character['health'] = character['max_health']
        print(f"\nLEVEL UP! Now level {character['level']}")

    return character['level']


def add_gold(character, amount):
    """Add gold to character"""
    if character['gold'] + amount < 0:
        raise ValueError("Not enough gold")
    character['gold'] += amount
    return character['gold']


def heal_character(character, amount):
    """Heal character by specified amount"""
    if is_character_dead(character):
        return 0

    old_health = character['health']
    character['health'] = min(character['health'] + amount, character['max_health'])
    return character['health'] - old_health


def is_character_dead(character):
    """Check if character's health is 0 or below"""
    return character['health'] <= 0


def revive_character(character):
    """Revive a dead character with 50% health"""
    if not is_character_dead(character):
        return False
    character['health'] = character['max_health'] // 2
    return True


# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """Validate character dictionary has required fields"""
    required = [
        ('name', str), ('class', str), ('level', int), ('health', int),
        ('max_health', int), ('strength', int), ('magic', int),
        ('experience', int), ('gold', int), ('inventory', list),
        ('active_quests', list), ('completed_quests', list)
    ]

    for field, field_type in required:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")
        if not isinstance(character[field], field_type):
            raise InvalidSaveDataError(f"Field '{field}' has wrong type")

    return True
