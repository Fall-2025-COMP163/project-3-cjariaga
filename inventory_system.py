"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Clayan Ariaga

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory.
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full! Cannot pick up item.")
        
    character['inventory'].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory.
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    try:
        character['inventory'].remove(item_id)
        return True
    except ValueError:
        raise ItemNotFoundError(f"Item ID '{item_id}' not found in inventory.")

def has_item(character, item_id, quantity=1):
    """
    Check if character has the required quantity of an item.
    
    Returns: True if character has item, False otherwise.
    """
    return character['inventory'].count(item_id) >= quantity

def use_item(character, item_id, all_items):
    """
    Use a consumable item.
    
    Args:
        character: Character dictionary
        item_id: Item to use (must be consumable)
        all_items: Dictionary of all item data
    
    Returns: True if used successfully
    Raises: 
        ItemNotFoundError if item not in inventory or not in all_items
        InvalidItemTypeError if item is not consumable
    """
    # 1. Check if item exists in all_items
    item_data = all_items.get(item_id)
    if not item_data:
        # Item exists in inventory but not in master data, treat as not found/corrupted data
        raise ItemNotFoundError(f"Item data for ID '{item_id}' not found.")
        
    # 2. Check if item is in inventory
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"You do not have a '{item_data['NAME']}' to use.")
        
    # 3. Check item type
    if item_data['TYPE'] != 'consumable':
        raise InvalidItemTypeError(f"Item '{item_data['NAME']}' is a {item_data['TYPE']} and cannot be 'used' this way.")
        
    # 4. Apply effect and remove item
    effect_str = item_data['EFFECT']
    effect_stat, effect_value = effect_str.split(':')
    effect_value = int(effect_value)
    
    apply_stat_effect(character, effect_stat, effect_value)
    remove_item_from_inventory(character, item_id)
    
    print(f"✨ Used {item_data['NAME']}. {effect_stat.capitalize()} restored by {effect_value}.")
    
    return True

def apply_stat_effect(character, stat_name, value):
    """
    Apply a positive stat change to the character.
    
    Ensures health cannot exceed max_health.
    """
    if stat_name == 'health':
        character['health'] += value
        if character['health'] > character['max_health']:
            character['health'] = character['max_health']
            
    elif stat_name == 'magic':
        # Placeholder for future mana system
        character['magic'] += value
        print(f"(Magic Stat Increased: +{value})")
        
    elif stat_name == 'strength':
        character['strength'] += value
        print(f"(Strength Stat Increased: +{value})")
        
    elif stat_name == 'max_health':
        character['max_health'] += value
        character['health'] += value # Also heal for the amount
        
    else:
        # For development, just print a warning for unhandled stats
        print(f"Warning: Unhandled stat effect applied: {stat_name}:{value}")
        
def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way.
    """
    inventory_counts = {}
    for item_id in character['inventory']:
        inventory_counts[item_id] = inventory_counts.get(item_id, 0) + 1
        
    print("\n==================== INVENTORY ====================")
    print(f"Gold: {character['gold']}")
    if not inventory_counts:
        print("Inventory is empty.")
        
    for item_id, count in inventory_counts.items():
        item_name = item_data_dict.get(item_id, {}).get('NAME', item_id)
        item_type = item_data_dict.get(item_id, {}).get('TYPE', 'Unknown')
        print(f" - {item_name} (x{count}) [{item_type.capitalize()}]")
        
    print("===================================================")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    from game_data import load_items, create_default_data_files
    
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Setup data
    create_default_data_files()
    try:
        test_items = load_items()
    except Exception as e:
        print(f"Could not load items: {e}")
        test_items = {}
        
    test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80, 'strength': 10, 'magic': 5}
    
    # 1. Test adding items
    try:
        add_item_to_inventory(test_char, "health_potion")
        add_item_to_inventory(test_char, "health_potion")
        add_item_to_inventory(test_char, "rusty_sword")
        print(f"Inventory after adding: {test_char['inventory']}")
    except InventoryFullError:
        print("Inventory is full! (Error)")
        
    # 2. Test removal and display
    display_inventory(test_char, test_items)
    
    try:
        remove_item_from_inventory(test_char, "rusty_sword")
        print(f"Inventory after removing sword: {test_char['inventory']}")
    except ItemNotFoundError:
        print("Item not found. (Error)")
        
    # 3. Test using items
    original_health = test_char['health'] = 50
    try:
        use_item(test_char, "health_potion", test_items)
        print(f"Health after potion: {test_char['health']} (was {original_health})")
    except ItemNotFoundError as e:
        print(f"Use item error: {e}")
    except InvalidItemTypeError as e:
        print(f"Use item error: {e}")
        
    # 4. Test max health cap
    test_char['health'] = test_char['max_health']
    try:
        use_item(test_char, "health_potion", test_items)
        print(f"Health should be max: {test_char['health']}/{test_char['max_health']}")
    except Exception:
        pass # Should pass silently
