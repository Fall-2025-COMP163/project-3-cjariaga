"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: Clayan Ariaga

AI Usage: Gemini, was used in the creating the
entire user interface, game loop, and menu systems. I integrated all
other modules (character_manager, inventory_system, etc.), handling
their specific exceptions with try-except blocks to create a robust
and user-friendly command-line application.

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

import sys
import os
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

current_character = None
all_quests = {}
all_items = {}
game_running = False


# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """Display main menu and get choice"""
    print("\n=== QUEST CHRONICLES ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")
    choice = input("Choice: ").strip()
    return int(choice) if choice.isdigit() else 0


def new_game():
    """Start a new game"""
    global current_character

    name = input("\nCharacter name: ").strip()
    print("\nClasses: 1=Warrior 2=Mage 3=Rogue 4=Cleric")
    class_choice = input("Choice: ").strip()

    classes = {'1': 'Warrior', '2': 'Mage', '3': 'Rogue', '4': 'Cleric'}
    char_class = classes.get(class_choice, 'Warrior')

    try:
        current_character = character_manager.create_character(name, char_class)
        save_game()
        game_loop()
    except InvalidCharacterClassError as e:
        print(f"Error: {e}")


def load_game():
    """Load an existing game"""
    global current_character

    saves = character_manager.list_saved_characters()
    if not saves:
        print("No saved games found.")
        return

    print("\nSaved characters:")
    for i, name in enumerate(saves, 1):
        print(f"{i}. {name}")

    choice = input("Select character: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(saves):
        try:
            current_character = character_manager.load_character(saves[int(choice) - 1])
            game_loop()
        except (CharacterNotFoundError, SaveFileCorruptedError) as e:
            print(f"Error: {e}")


# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """Main game loop"""
    global game_running, current_character
    game_running = True

    while game_running:
        try:
            if character_manager.is_character_dead(current_character):
                raise CharacterDeadError("You died!")

            choice = game_menu()

            if choice == 1:
                view_stats()
            elif choice == 2:
                view_inventory()
            elif choice == 3:
                quest_menu()
            elif choice == 4:
                explore()
            elif choice == 5:
                shop()
            elif choice == 6:
                save_game()
                game_running = False
                current_character = None

            if game_running:
                save_game()

        except CharacterDeadError:
            print("\n=== YOU DIED ===")
            print(f"Revive for 50 gold? You have {current_character['gold']}")
            if input("(y/n): ").lower() == 'y':
                try:
                    character_manager.add_gold(current_character, -50)
                    character_manager.revive_character(current_character)
                    print("Revived!")
                except ValueError:
                    print("Not enough gold. Game over.")
                    game_running = False
                    current_character = None
            else:
                game_running = False
                current_character = None


def game_menu():
    """Display game menu"""
    print(f"\n=== {current_character['name']} Lv.{current_character['level']} ===")
    print(f"HP: {current_character['health']}/{current_character['max_health']} | Gold: {current_character['gold']}")
    print("1. Stats  2. Inventory  3. Quests  4. Explore  5. Shop  6. Save & Quit")
    choice = input("Choice: ").strip()
    return int(choice) if choice.isdigit() else 0


# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_stats():
    """View character stats"""
    c = current_character
    print(f"\n{c['name']} - {c['class']} Lv.{c['level']}")
    print(f"HP: {c['health']}/{c['max_health']}")
    print(f"STR: {c['strength']} | MAG: {c['magic']}")
    print(f"XP: {c['experience']}/{c['level'] * 100}")
    print(f"Gold: {c['gold']}")

    weapon = c.get('equipped_weapon')
    armor = c.get('equipped_armor')
    print(f"Weapon: {all_items.get(weapon, {}).get('name', 'None') if weapon else 'None'}")
    print(f"Armor: {all_items.get(armor, {}).get('name', 'None') if armor else 'None'}")

    print(f"\nActive quests: {len(c['active_quests'])}")
    print(f"Completed: {len(c['completed_quests'])}")
    input("\nPress Enter...")


def view_inventory():
    """View and manage inventory"""
    while True:
        inventory_system.display_inventory(current_character, all_items)
        print("\n1. Use  2. Equip  3. Unequip  4. Back")
        choice = input("Choice: ").strip()

        try:
            if choice == '1':
                item_id = input("Item ID: ").strip()
                inventory_system.use_item(current_character, item_id, all_items)
                print("Used!")
            elif choice == '2':
                item_id = input("Item ID: ").strip()
                if all_items[item_id]['type'] == 'weapon':
                    inventory_system.equip_weapon(current_character, item_id, all_items)
                else:
                    inventory_system.equip_armor(current_character, item_id, all_items)
                print("Equipped!")
            elif choice == '3':
                item_type = input("'weapon' or 'armor': ").strip()
                if item_type == 'weapon':
                    inventory_system.unequip_weapon(current_character, all_items)
                else:
                    inventory_system.unequip_armor(current_character, all_items)
                print("Unequipped!")
            elif choice == '4':
                break
        except (InventoryError, ItemNotFoundError) as e:
            print(f"Error: {e}")


def quest_menu():
    """Quest management"""
    while True:
        print("\n1. Active  2. Available  3. Completed  4. Accept  5. Abandon  6. Back")
        choice = input("Choice: ").strip()

        try:
            if choice == '1':
                quests = quest_handler.get_active_quests(current_character, all_quests)
                for q in quests:
                    print(f"[{q['quest_id']}] {q['title']}")
            elif choice == '2':
                quests = quest_handler.get_available_quests(current_character, all_quests)
                for q in quests:
                    print(f"[{q['quest_id']}] {q['title']} (Lv {q['required_level']})")
            elif choice == '3':
                quests = quest_handler.get_completed_quests(current_character, all_quests)
                for q in quests:
                    print(f"[{q['quest_id']}] {q['title']}")
            elif choice == '4':
                quest_id = input("Quest ID: ").strip()
                quest_handler.accept_quest(current_character, quest_id, all_quests)
                print("Accepted!")
            elif choice == '5':
                quest_id = input("Quest ID: ").strip()
                quest_handler.abandon_quest(current_character, quest_id)
                print("Abandoned!")
            elif choice == '6':
                break
        except (QuestError, InsufficientLevelError) as e:
            print(f"Error: {e}")

        input("\nPress Enter...")


def explore():
    """Find and fight enemies"""
    enemy = combat_system.get_random_enemy_for_level(current_character['level'])
    battle = combat_system.SimpleBattle(current_character, enemy)

    try:
        result = battle.start_battle()
        if result['winner'] == 'player':
            print(f"\nVictory! +{result['xp']} XP, +{result['gold']} gold")
    except CharacterDeadError:
        raise


def shop():
    """Buy and sell items"""
    while True:
        print(f"\n=== SHOP === Gold: {current_character['gold']}")
        print("1. Buy  2. Sell  3. Back")
        choice = input("Choice: ").strip()

        try:
            if choice == '1':
                print("\nItems:")
                for item_id, item in all_items.items():
                    print(f"[{item_id}] {item['name']} - {item['cost']}g")
                item_id = input("\nBuy: ").strip()
                inventory_system.purchase_item(current_character, item_id, all_items)
                print("Purchased!")
            elif choice == '2':
                inventory_system.display_inventory(current_character, all_items)
                item_id = input("\nSell: ").strip()
                gold = inventory_system.sell_item(current_character, item_id, all_items)
                print(f"Sold for {gold} gold!")
            elif choice == '3':
                break
        except (InventoryError, InsufficientResourcesError) as e:
            print(f"Error: {e}")


# ============================================================================
# SAVE/LOAD
# ============================================================================

def save_game():
    """Save current game"""
    if current_character:
        character_manager.save_character(current_character)


def load_game_data():
    """Load quest and item data"""
    global all_quests, all_items

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
        quest_handler.validate_quest_prerequisites(all_quests)
    except MissingDataFileError:
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    print("=== QUEST CHRONICLES ===")
    load_game_data()

    while True:
        choice = main_menu()
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
