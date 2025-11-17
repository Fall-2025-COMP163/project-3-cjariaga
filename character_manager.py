"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module

This module handles character creation, loading, and saving.
"""

import os
import json
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError,
    InsufficientResourcesError
)

# Base stats for each class
BASE_STATS = {
    'Warrior': {'health': 120, 'strength': 15, 'magic': 5},
    'Mage':    {'health': 80,  'strength': 8,  'magic': 20},
    'Rogue':   {'health': 90,  'strength': 12, 'magic': 10},
    'Cleric':  {'health': 100, 'strength': 10, 'magic': 15}
}

# XP required for the next level (simple progression)
XP_TO_NEXT_LEVEL = {
    1: 100, 2: 250, 3: 500, 4: 800, 5: 1200, 6: 1800, 7: 2500, 8: 3500, 9: 5000, 10: 99999
}

# Stat gain per level
LEVEL_UP_STATS = {
    'Warrior': {'health': 20, 'strength': 3, 'magic': 1},
    'Mage':    {'health': 10, 'strength': 1, 'magic': 3},
    'Rogue':   {'health': 15, 'strength': 2, 'magic': 2},
    'Cleric':  {'health': 18, 'strength': 2, 'magic': 2}
}

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class.
    
    Returns: Dictionary with character data.
    Raises: InvalidCharacterClassError if class is not valid.
    """
    if character_class not in BASE_STATS:
        raise InvalidCharacterClassError(f"Class '{character_class}' is not a valid character class.")
        
    base_health = BASE_STATS[character_class]['health']
    
    character = {
        'name': name,
        'class': character_class,
        'level': 1,
        'health': base_health,
        'max_health': base_health,
        'strength': BASE_STATS[character_class]['strength'],
        'magic': BASE_STATS[character_class]['magic'],
        'experience': 0,
        'gold': 100,
        'inventory': ['health_potion', 'health_potion', 'rusty_sword'],
        'active_quests': [],
        'completed_quests': []
    }
    
    return character

def level_up(character):
    """
    Check if character can level up. If so, apply stat increases.
    
    Returns: True if leveled up, False otherwise.
    """
    current_xp = character['experience']
    current_level = character['level']
    char_class = character['class']
    
    if current_level in XP_TO_NEXT_LEVEL and current_xp >= XP_TO_NEXT_LEVEL[current_level]:
        # Perform level up
        character['level'] += 1
        gain = LEVEL_UP_STATS.get(char_class, {'health': 10, 'strength': 1, 'magic': 1})
        
        character['max_health'] += gain['health']
        character['health'] = character['max_health'] # Full heal on level up
        character['strength'] += gain['strength']
        character['magic'] += gain['magic']
        
        print("===================================")
        print(f"🎉 {character['name']} LEVELED UP to Level {character['level']}! 🎉")
        print(f"Stats increased: HP +{gain['health']}, STR +{gain['strength']}, MAG +{gain['magic']}")
        print("===================================")
        
        return True
    return False

def revive_character(character):
    """
    Revives a dead character at a cost.
    
    Returns: True if revived.
    Raises: InsufficientResourcesError if not enough gold.
    """
    revive_cost = 50 * character['level']
    
    if character['health'] > 0:
        return False # Not dead
        
    if character['gold'] < revive_cost:
        raise InsufficientResourcesError(f"Cannot afford revival. Cost: {revive_cost} gold.")
        
    character['gold'] -= revive_cost
    character['health'] = character['max_health'] // 2 # Half health upon revival
    
    print(f"\n✨ {character['name']} revived for {revive_cost} gold! Health restored to {character['health']}.")
    return True

# ============================================================================
# SAVE/LOAD FUNCTIONS
# ============================================================================

def get_save_filepath(character_name):
    """Return the standardized filepath for a character's save file."""
    save_dir = "saves"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return os.path.join(save_dir, f"{character_name.lower().replace(' ', '_')}.json")

def save_character(character):
    """
    Save character data to a JSON file.
    
    Raises: InvalidSaveDataError if data is clearly invalid before saving.
    """
    if not validate_save_data(character):
        # validate_save_data will raise the specific error
        pass
        
    filepath = get_save_filepath(character['name'])
    
    try:
        with open(filepath, 'w') as f:
            json.dump(character, f, indent=4)
    except Exception as e:
        print(f"Error saving file: {e}")
        # Could raise a custom I/O error here if needed
        
def load_character(character_name):
    """
    Load character data from a JSON file.
    
    Returns: Dictionary with character data
    Raises: CharacterNotFoundError, SaveFileCorruptedError, InvalidSaveDataError
    """
    filepath = get_save_filepath(character_name)
    
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"No save file found for '{character_name}'.")
        
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise SaveFileCorruptedError("Save file is corrupted (JSON format error).")
    except Exception as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")
        
    if not validate_save_data(data):
        # validate_save_data will raise the specific error
        pass
        
    return data

def validate_save_data(data):
    """
    Validate that the loaded data structure is sound.
    
    Required fields: name, class, level, health, max_health, 
                    strength, magic, experience, gold, inventory,
                    active_quests, completed_quests
    
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    required_fields = {
        'name': str, 'class': str, 'level': int, 'health': int, 'max_health': int, 
        'strength': int, 'magic': int, 'experience': int, 'gold': int, 
        'inventory': list, 'active_quests': list, 'completed_quests': list
    }
    
    if not isinstance(data, dict):
        raise InvalidSaveDataError("Save data is not a dictionary.")
        
    for field, expected_type in required_fields.items():
        if field not in data:
            raise InvalidSaveDataError(f"Missing required field: '{field}'")
        if not isinstance(data[field], expected_type):
            # Special check for lists to ensure they're not just strings/tuples/etc.
            if expected_type == list and not isinstance(data[field], list):
                 raise InvalidSaveDataError(f"Field '{field}' has wrong type. Expected {expected_type}, got {type(data[field])}")
            # Numeric types should not be strings
            if expected_type in (int, float) and isinstance(data[field], str):
                 raise InvalidSaveDataError(f"Field '{field}' has wrong type. Expected number, got string.")
        
    # Additional logic checks
    if data['class'] not in BASE_STATS:
        raise InvalidSaveDataError(f"Invalid character class: {data['class']}")
    if data['health'] > data['max_health']:
        data['health'] = data['max_health'] # Self-correcting for safety
    if data['level'] < 1:
        data['level'] = 1 # Self-correcting for safety
        
    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # 1. Test character creation (valid)
    try:
        warrior = create_character("TestHero", "Warrior")
        print(f"Created: {warrior['name']} the {warrior['class']}")
        print(f"Stats: HP={warrior['health']}, STR={warrior['strength']}, MAG={warrior['magic']}")
    except InvalidCharacterClassError as e:
        print(f"Invalid class: {e}")
    
    # 2. Test character creation (invalid)
    try:
        create_character("BadHero", "Wizard")
    except InvalidCharacterClassError as e:
        print(f"Successfully caught invalid class: {e}")
        
    # 3. Test saving
    try:
        save_character(warrior)
        print("Character saved successfully")
    except Exception as e:
        print(f"Save error: {e}")
    
    # 4. Test loading
    try:
        loaded = load_character("TestHero")
        print(f"Loaded: {loaded['name']} (Level {loaded['level']})")
    except CharacterNotFoundError:
        print("Character not found (Error)")
    except SaveFileCorruptedError:
        print("Save file corrupted (Error)")
    except InvalidSaveDataError as e:
        print(f"Invalid Save Data (Error): {e}")
        
    # 5. Test level up
    warrior['experience'] = XP_TO_NEXT_LEVEL[1] + 10 # Give enough XP
    level_up(warrior)
    print(f"Post-Level: Level {warrior['level']}, Max HP {warrior['max_health']}, STR {warrior['strength']}")
    
    # 6. Test revive
    warrior['health'] = 0
    warrior['gold'] = 1000
    try:
        revive_character(warrior)
        print(f"Revived: Health is {warrior['health']}, Gold is {warrior['gold']}")
    except InsufficientResourcesError as e:
        print(f"Revive error: {e}")
