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
# HELPERS
# ============================================================================
def _resolve_item(item_id, item_data):
    """Resolve item metadata.
    Accepts either:
      - item_data as a dict representing the single item
      - item_data as mapping {item_id: {...}, ...}
    Returns the item dict or raises ItemNotFoundError.
    """
    if item_data is None:
        raise ItemNotFoundError(f"No item data provided for '{item_id}'.")

    if isinstance(item_data, dict) and 'type' in item_data and (item_data.get('id') == item_id or True):
        # Heuristic: if the provided dict looks like an item (has 'type'), treat as the item itself
        return item_data
    # Otherwise, expect mapping
    if item_id not in item_data:
        raise ItemNotFoundError(f"Item data for '{item_id}' not found.")
    return item_data[item_id]


# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================
def add_item_to_inventory(character, item_id):
    """Add an item to character's inventory"""
    if 'inventory' not in character or character['inventory'] is None:
        character['inventory'] = []
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Your inventory is full!")
    character['inventory'].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """Remove an item from character's inventory"""
    if 'inventory' not in character or character['inventory'] is None:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    try:
        character['inventory'].remove(item_id)
        return True
    except ValueError:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")


def has_item(character, item_id):
    """Check if character has a specific item"""
    return item_id in character.get('inventory', [])


def count_item(character, item_id):
    """Count how many of a specific item the character has"""
    return character.get('inventory', []).count(item_id)


def get_inventory_space_remaining(character):
    """Calculate remaining inventory space"""
    return MAX_INVENTORY_SIZE - len(character.get('inventory', []))


# ============================================================================
# ITEM USAGE
# ============================================================================
def use_item(character, item_id, item_data):
    """Use a consumable item."""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")

    item = _resolve_item(item_id, item_data)
    if item.get('type') != 'consumable':
        raise InvalidItemTypeError(f"{item.get('name', item_id)} is not consumable.")

    effect = item.get('effect')
    if not effect or ':' not in effect:
        raise InvalidItemTypeError(f"Malformed effect for {item.get('name', item_id)}")

    stat, value_str = effect.split(':', 1)
    stat = stat.strip()
    try:
        value = int(value_str.strip())
    except ValueError:
        raise InvalidItemTypeError(f"Invalid effect value for {item.get('name', item_id)}")

    if stat == 'health':
        healed = character_manager.heal_character(character, value)
    elif stat == 'strength':
        character['strength'] = character.get('strength', 0) + value
        healed = 0
    elif stat == 'magic':
        character['magic'] = character.get('magic', 0) + value
        healed = 0
    elif stat == 'max_health':
        character['max_health'] = character.get('max_health', 0) + value
        # Optionally heal the same amount to current health
        character['health'] = min(character.get('health', 0) + value, character['max_health'])
        healed = value
    else:
        raise InvalidItemTypeError(f"Unknown stat '{stat}' for {item.get('name', item_id)}")

    remove_item_from_inventory(character, item_id)
    return f"Used {item.get('name', item_id)}"


def equip_weapon(character, item_id, item_data):
    """Equip a weapon"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    item = _resolve_item(item_id, item_data)
    if item.get('type') != 'weapon':
        raise InvalidItemTypeError(f"{item.get('name', item_id)} is not a weapon.")

    # Unequip old weapon
    if character.get('equipped_weapon'):
        # ensure space for unequipped item
        if get_inventory_space_remaining(character) < 1:
            raise InventoryFullError("Inventory full, cannot unequip old weapon.")
        unequip_weapon(character, item_data)

    # Remove from inventory and equip
    remove_item_from_inventory(character, item_id)

    # Apply stat bonus, safe parsing
    effect = item.get('effect', '')
    if ':' in effect:
        stat, value_str = effect.split(':', 1)
        try:
            value = int(value_str.strip())
        except ValueError:
            value = 0
        stat = stat.strip()
        if stat == 'max_health':
            character['max_health'] = character.get('max_health', 0) + value
            character['health'] = min(character.get('health', 0) + value, character['max_health'])
        else:
            character[stat] = character.get(stat, 0) + value

    character['equipped_weapon'] = item_id
    return f"Equipped {item.get('name', item_id)}"


def equip_armor(character, item_id, item_data):
    """Equip armor"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    item = _resolve_item(item_id, item_data)
    if item.get('type') != 'armor':
        raise InvalidItemTypeError(f"{item.get('name', item_id)} is not armor.")

    # Unequip old armor
    if character.get('equipped_armor'):
        if get_inventory_space_remaining(character) < 1:
            raise InventoryFullError("Inventory full, cannot unequip old armor.")
        unequip_armor(character, item_data)

    remove_item_from_inventory(character, item_id)

    effect = item.get('effect', '')
    if ':' in effect:
        stat, value_str = effect.split(':', 1)
        try:
            value = int(value_str.strip())
        except ValueError:
            value = 0
        stat = stat.strip()
        if stat == 'max_health':
            character['max_health'] = character.get('max_health', 0) + value
            character['health'] = min(character.get('health', 0) + value, character['max_health'])
        else:
            character[stat] = character.get(stat, 0) + value

    character['equipped_armor'] = item_id
    return f"Equipped {item.get('name', item_id)}"


def unequip_weapon(character, item_data):
    """Unequip weapon and return to inventory"""
    weapon_id = character.get('equipped_weapon')
    if not weapon_id:
        return "No weapon equipped"

    if get_inventory_space_remaining(character) < 1:
        raise InventoryFullError("Inventory full")

    item = _resolve_item(weapon_id, item_data)

    # Remove stat bonus if present
    effect = item.get('effect', '')
    if ':' in effect:
        stat, value_str = effect.split(':', 1)
        try:
            value = int(value_str.strip())
        except ValueError:
            value = 0
        stat = stat.strip()
        if stat == 'max_health':
            character['max_health'] = max(0, character.get('max_health', 0) - value)
            character['health'] = min(character.get('health', 0), character['max_health'])
        else:
            character[stat] = character.get(stat, 0) - value

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

    item = _resolve_item(armor_id, item_data)

    # Remove stat bonus if present
    effect = item.get('effect', '')
    if ':' in effect:
        stat, value_str = effect.split(':', 1)
        try:
            value = int(value_str.strip())
        except ValueError:
            value = 0
        stat = stat.strip()
        if stat == 'max_health':
            character['max_health'] = max(0, character.get('max_health', 0) - value)
            character['health'] = min(character.get('health', 0), character['max_health'])
        else:
            character[stat] = character.get(stat, 0) - value

    add_item_to_inventory(character, armor_id)
    character['equipped_armor'] = None
    return f"Unequipped {item.get('name', armor_id)}"


# ============================================================================
# SHOP SYSTEM
# ============================================================================
def purchase_item(character, item_id, item_data):
    """Purchase an item from shop."""
    item = _resolve_item(item_id, item_data)
    cost = int(item.get('cost', 0))
    if character.get('gold', 0) < cost:
        raise InsufficientResourcesError(f"Need {cost} gold, have {character.get('gold', 0)}.")

    add_item_to_inventory(character, item_id)
    character_manager.add_gold(character, -cost)
    return f"Purchased {item.get('name', item_id)}"


def sell_item(character, item_id, item_data):
    """Sell an item for half cost - returns gold amount as integer"""
    item = _resolve_item(item_id, item_data)
    remove_item_from_inventory(character, item_id)
    sell_price = int(item.get('cost', 0)) // 2
    character_manager.add_gold(character, sell_price)
    return sell_price


# ============================================================================
# DISPLAY
# ============================================================================
def display_inventory(character, item_data=None):
    """Display character's inventory safely."""
    inv = character.get('inventory', [])
    print(f"\n--- INVENTORY ({len(inv)}/{MAX_INVENTORY_SIZE}) ---")
    print(f"Gold: {character.get('gold', 0)}")

    weapon_id = character.get('equipped_weapon')
    armor_id = character.get('equipped_armor')
    weapon_name = "None"
    armor_name = "None"
    if weapon_id and item_data:
        try:
            weapon = _resolve_item(weapon_id, item_data)
            weapon_name = weapon.get('name', weapon_id)
        except ItemNotFoundError:
            weapon_name = weapon_id
    if armor_id and item_data:
        try:
            armor = _resolve_item(armor_id, item_data)
            armor_name = armor.get('name', armor_id)
        except ItemNotFoundError:
            armor_name = armor_id

    print(f"Weapon: {weapon_name}")
    print(f"Armor: {armor_name}")

    if inv:
        item_counts = {}
        for item_id in inv:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        print("\nItems:")
        for item_id, count in item_counts.items():
            name = item_id
            if item_data:
                try:
                    name = _resolve_item(item_id, item_data).get('name', item_id)
                except ItemNotFoundError:
                    name = item_id
            print(f"  {name} x{count}")
