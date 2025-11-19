"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Clayan Ariaga

AI Usage: I used AI assistance to help structure the inventory management system,
debug test compatibility issues, and ensure proper exception handling. The AI
helped me understand how to properly store equipment data and return values
that match test expectations.

This module handles inventory management, item usage, and equipment.
"""


from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)
import character_manager

MAX_INVENTORY_SIZE = 20


# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """Add an item to character's inventory"""
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Your inventory is full!")
    character['inventory'].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """Remove an item from character's inventory"""
    try:
        character['inventory'].remove(item_id)
        return True
    except ValueError:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")


def has_item(character, item_id):
    """Check if character has a specific item"""
    return item_id in character['inventory']


def count_item(character, item_id):
    """Count how many of a specific item the character has"""
    return character['inventory'].count(item_id)


def get_inventory_space_remaining(character):
    """Calculate remaining inventory space"""
    return MAX_INVENTORY_SIZE - len(character['inventory'])


# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """Use a consumable item"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    # Handle both dict of items and single item dict
    if 'type' in item_data:
        item = item_data
    else:
        if item_id not in item_data:
            raise ItemNotFoundError(f"Item data for '{item_id}' not found.")
        item = item_data[item_id]

    if item['type'] != 'consumable':
        raise InvalidItemTypeError(f"{item.get('name', item_id)} is not consumable.")

    # Apply effect
    stat, value = item['effect'].split(':')
    stat = stat.strip()
    value = int(value.strip())

    if stat == 'health':
        character_manager.heal_character(character, value)
    elif stat == 'strength':
        character['strength'] += value
    elif stat == 'magic':
        character['magic'] += value

    remove_item_from_inventory(character, item_id)
    return f"Used {item.get('name', item_id)}"


def equip_weapon(character, item_id, item_data):
    """Equip a weapon"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if 'type' in item_data:
        item = item_data
    else:
        if item_id not in item_data:
            raise ItemNotFoundError(f"Item data for '{item_id}' not found.")
        item = item_data[item_id]

    if item['type'] != 'weapon':
        raise InvalidItemTypeError(f"{item.get('name', item_id)} is not a weapon.")

    # Unequip old weapon if exists
    if character.get('equipped_weapon'):
        if get_inventory_space_remaining(character) < 1:
            raise InventoryFullError("Inventory full, cannot unequip old weapon.")
        unequip_weapon(character, item_data)

    # Remove from inventory and equip
    remove_item_from_inventory(character, item_id)

    # Apply stat bonus
    stat, value = item['effect'].split(':')
    value = int(value.strip())
    character[stat.strip()] += value

    character['equipped_weapon'] = item_id
    return f"Equipped {item.get('name', item_id)}"


def equip_armor(character, item_id, item_data):
    """Equip armor"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    if 'type' in item_data:
        item = item_data
    else:
        if item_id not in item_data:
            raise ItemNotFoundError(f"Item data for '{item_id}' not found.")
        item = item_data[item_id]

    if item['type'] != 'armor':
        raise InvalidItemTypeError(f"{item.get('name', item_id)} is not armor.")

    # Unequip old armor if exists
    if character.get('equipped_armor'):
        if get_inventory_space_remaining(character) < 1:
            raise InventoryFullError("Inventory full, cannot unequip old armor.")
        unequip_armor(character, item_data)

    # Remove from inventory and equip
    remove_item_from_inventory(character, item_id)

    # Apply stat bonus
    stat, value = item['effect'].split(':')
    value = int(value.strip())
    if stat.strip() == 'max_health':
        character['max_health'] += value
        character['health'] += value
    else:
        character[stat.strip()] += value

    character['equipped_armor'] = item_id
    return f"Equipped {item.get('name', item_id)}"


def unequip_weapon(character, item_data):
    """Unequip weapon and return to inventory"""
    weapon_id = character.get('equipped_weapon')
    if not weapon_id:
        return "No weapon equipped"

    if get_inventory_space_remaining(character) < 1:
        raise InventoryFullError("Inventory full")

    if 'type' in item_data:
        item = item_data
    else:
        item = item_data.get(weapon_id, {})

    # Remove stat bonus
    if 'effect' in item:
        stat, value = item['effect'].split(':')
        value = int(value.strip())
        character[stat.strip()] -= value

    add_item_to_inventory(character, weapon_id)
    character['equipped_weapon'] = None
    return f"Unequipped {item.get('name', weapon_id)}"


def unequip_armor(character, item_data):
    """Unequip armor and return to inventory"""
    armor_id = character.get('equipped_armor')
    if not armor_id:
        return "No armor equipped"

    if get_inventory_space_remaining(character) < 1:
        raise InventoryFullError("Inventory full")

    if 'type' in item_data:
        item = item_data
    else:
        item = item_data.get(armor_id, {})

    # Remove stat bonus
    if 'effect' in item:
        stat, value = item['effect'].split(':')
        value = int(value.strip())
        if stat.strip() == 'max_health':
            character['max_health'] -= value
            character['health'] = min(character['health'], character['max_health'])
        else:
            character[stat.strip()] -= value

    add_item_to_inventory(character, armor_id)
    character['equipped_armor'] = None
    return f"Unequipped {item.get('name', armor_id)}"


# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """Purchase an item from shop"""
    if 'cost' in item_data:
        item = item_data
    else:
        if item_id not in item_data:
            raise ItemNotFoundError(f"Item '{item_id}' not in shop.")
        item = item_data[item_id]

    if character['gold'] < item['cost']:
        raise InsufficientResourcesError(f"Need {item['cost']} gold, have {character['gold']}.")

    add_item_to_inventory(character, item_id)
    character_manager.add_gold(character, -item['cost'])
    return f"Purchased {item.get('name', item_id)}"


def sell_item(character, item_id, item_data):
    """Sell an item for half cost - returns gold amount as integer"""
    if 'cost' in item_data:
        item = item_data
    else:
        if item_id not in item_data:
            raise ItemNotFoundError(f"Item data for '{item_id}' not found.")
        item = item_data[item_id]

    remove_item_from_inventory(character, item_id)
    sell_price = item['cost'] // 2
    character_manager.add_gold(character, sell_price)
    return sell_price


# ============================================================================
# DISPLAY
# ============================================================================

def display_inventory(character, item_data):
    """Display character's inventory"""
    print(f"\n--- INVENTORY ({len(character['inventory'])}/{MAX_INVENTORY_SIZE}) ---")
    print(f"Gold: {character['gold']}")

    weapon_id = character.get('equipped_weapon')
    armor_id = character.get('equipped_armor')
    print(f"Weapon: {item_data.get(weapon_id, {}).get('name', 'None') if weapon_id else 'None'}")
    print(f"Armor: {item_data.get(armor_id, {}).get('name', 'None') if armor_id else 'None'}")

    if character['inventory']:
        item_counts = {}
        for item_id in character['inventory']:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        print("\nItems:")
        for item_id, count in item_counts.items():
            name = item_data.get(item_id, {}).get('name', item_id)
            print(f"  {name} x{count}")
