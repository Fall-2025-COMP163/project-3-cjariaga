"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *
import time

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# INITIALIZATION
# ============================================================================

def load_game_data():
    """Load all static game data and validate prerequisites."""
    global all_quests, all_items
    all_quests = game_data.load_quests()
    all_items = game_data.load_items()
    quest_handler.validate_quest_prerequisites(all_quests)
    # Check for other data issues here if needed
    
def get_valid_input(prompt, valid_options):
    """Utility to get and validate user input."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_options:
            return choice
        print(f"Invalid input. Please choose one of: {', '.join(valid_options)}")

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display main menu and get player choice.
    
    Returns: Integer choice (1-3)
    """
    print("\n--- MAIN MENU ---")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")
    
    choice = get_valid_input("Enter choice (1-3): ", ['1', '2', '3'])
    return int(choice)

def new_game():
    """
    Start a new game.
    
    Prompts for character name and class, creates character, and starts game loop.
    """
    global current_character, game_running
    
    name = input("Enter your hero's name: ").strip()
    
    print("\nAvailable Classes:")
    print(" - Warrior (High HP/STR)")
    print(" - Mage (High MAG)")
    print(" - Rogue (Medium STR/MAG)")
    print(" - Cleric (Medium HP/STR/MAG)")
    
    valid_classes = [c.lower() for c in character_manager.BASE_STATS.keys()]
    class_choice = get_valid_input("Choose your class: ", valid_classes)
    class_choice = class_choice.capitalize() # Convert to proper case for storage
    
    try:
        current_character = character_manager.create_character(name, class_choice)
        character_manager.save_character(current_character)
        print(f"\nWelcome, {current_character['name']} the {current_character['class']}!")
        print("Your adventure begins now!")
        game_running = True
        game_loop()
    except InvalidCharacterClassError as e:
        print(f"Error: {e}. Returning to main menu.")
    except Exception as e:
        print(f"An unexpected error occurred during creation: {e}")

def load_game():
    """
    Load an existing game.
    
    Prompts for character name and loads the save file.
    """
    global current_character, game_running
    
    name = input("Enter the hero's name to load: ").strip()
    
    try:
        current_character = character_manager.load_character(name)
        print(f"\nGame loaded successfully! Welcome back, {current_character['name']}!")
        game_running = True
        game_loop()
    except CharacterNotFoundError:
        print(f"Error: No save file found for '{name}'.")
    except SaveFileCorruptedError as e:
        print(f"Error: Save file for '{name}' is corrupted: {e}")
    except InvalidSaveDataError as e:
        print(f"Error: Save file for '{name}' contains invalid data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during loading: {e}")

# ============================================================================
# GAME LOOP AND LOCATIONS
# ============================================================================

def game_loop():
    """The main loop for an active game session."""
    global game_running
    
    while game_running:
        if current_character['health'] <= 0:
            handle_death()
            if not game_running: # Check if handle_death set to quit
                break
                
        print("\n" + "=" * 50)
        print(f"LOCATION: Town Square | {current_character['name']} (Lvl {current_character['level']})")
        print(f"HP: {current_character['health']}/{current_character['max_health']} | Gold: {current_character['gold']} | XP: {current_character['experience']}")
        print("=" * 50)
        
        # Check for level up after battle/quest reward
        character_manager.level_up(current_character)
        
        print("Available Actions:")
        print("1. Explore (Start Combat)")
        print("2. Quests")
        print("3. Inventory")
        print("4. Save & Quit")
        
        choice = get_valid_input("Enter action (1-4): ", ['1', '2', '3', '4'])
        
        if choice == '1':
            handle_combat()
        elif choice == '2':
            handle_quest_menu()
        elif choice == '3':
            handle_inventory_menu()
        elif choice == '4':
            character_manager.save_character(current_character)
            print("\nGame Saved. Goodbye!")
            game_running = False
            
        time.sleep(1) # Simple pause for better UX

def handle_death():
    """Handle character death state."""
    global game_running
    
    print("\n--- YOU HAVE DIED ---")
    print(f"Revival Cost: {50 * current_character['level']} Gold")
    
    options = ['revive', 'quit']
    choice = get_valid_input("Options: (Revive/Quit): ", options)
    
    if choice == 'revive':
        try:
            character_manager.revive_character(current_character)
            character_manager.save_character(current_character)
        except InsufficientResourcesError as e:
            print(f"Critical Error: {e}. You cannot afford revival and must quit.")
            choice = 'quit'
            
    if choice == 'quit':
        print("Returning to main menu...")
        game_running = False

def handle_combat():
    """Initiate and manage a battle."""
    global current_character
    
    print("\nSearching the wilderness...")
    time.sleep(1)
    
    # 1. Create a level-appropriate enemy
    try:
        enemy = combat_system.get_random_enemy_for_level(current_character['level'])
        battle = combat_system.SimpleBattle(current_character, enemy)
    except InvalidTargetError as e:
        print(f"Combat error: {e}")
        return
        
    # 2. Battle loop
    while battle.is_active:
        combat_system.display_combat_stats(current_character, enemy)
        
        print("Combat Options:")
        print("A. Attack")
        print("R. Run")
        # print("M. Use Magic/Ability (Placeholder)")
        
        choice = get_valid_input("Enter action (A/R): ", ['a', 'r'])
        
        try:
            if choice == 'a':
                battle_active = battle.attack()
            elif choice == 'r':
                if battle.run():
                    return # Fled successfully
                battle_active = battle.is_active
            
            # Check for win/loss conditions
            if not battle_active:
                if current_character['health'] > 0:
                    # Player won
                    rewards = combat_system.calculate_rewards(enemy)
                    print(f"\nVICTORY! Gained {rewards['xp']} XP and {rewards['gold']} Gold.")
                    current_character['experience'] += rewards['xp']
                    current_character['gold'] += rewards['gold']
                    
                    # Simple quest objective completion: Defeat 1 enemy = complete active quest
                    if current_character['active_quests']:
                        quest_id_to_complete = current_character['active_quests'][0]
                        try:
                            quest_handler.complete_quest(current_character, quest_id_to_complete, all_quests)
                        except Exception:
                            # Quest not ready for completion, this is fine
                            pass
                            
                # Save after battle
                character_manager.save_character(current_character)
                break
                
        except CharacterDeadError:
            # Player died during the run attempt
            character_manager.save_character(current_character)
            break
        except CombatNotActiveError:
            print("Combat loop error: Combat should be active but isn't.")
            break
        except Exception as e:
            print(f"Combat error: {e}")
            break

def handle_quest_menu():
    """Display active, completed, and available quests."""
    print("\n--- QUEST LOG ---")
    
    # Active Quests
    print("\nACTIVE QUESTS:")
    if current_character['active_quests']:
        for q_id in current_character['active_quests']:
            quest = all_quests.get(q_id, {'TITLE': 'UNKNOWN QUEST'})
            print(f"  - {quest['TITLE']}: {quest.get('DESCRIPTION', 'No description.')}")
    else:
        print("  - None active.")
        
    # Available Quests
    print("\nAVAILABLE QUESTS:")
    available_to_show = False
    for q_id, quest in all_quests.items():
        met_reqs, message = quest_handler.check_prerequisites(current_character, q_id, all_quests)
        if met_reqs:
            print(f"  - [{q_id}] {quest['TITLE']} (Ready!)")
            available_to_show = True
        elif not (q_id in current_character['completed_quests'] or q_id in current_character['active_quests']):
            # Only show unavailable if not already completed/active
            print(f"  - {quest['TITLE']} ({message})")
            available_to_show = True
            
    if not available_to_show:
        print("  - No new quests available.")

    # Menu
    print("\nQuest Options:")
    print("1. Accept Quest by ID")
    print("2. Back")
    
    choice = get_valid_input("Enter choice (1-2): ", ['1', '2'])
    
    if choice == '1':
        quest_id = input("Enter Quest ID to accept (e.g., tutorial_1): ").strip()
        try:
            if quest_handler.accept_quest(current_character, quest_id, all_quests):
                character_manager.save_character(current_character)
        except Exception as e:
            print(f"Quest Error: {e}")

def handle_inventory_menu():
    """Display inventory and options to use items."""
    
    inventory_system.display_inventory(current_character, all_items)
    
    print("\nInventory Options:")
    print("1. Use Item")
    print("2. Back")
    
    choice = get_valid_input("Enter choice (1-2): ", ['1', '2'])
    
    if choice == '1':
        item_id = input("Enter Item ID to use (e.g., health_potion): ").strip()
        try:
            if inventory_system.use_item(current_character, item_id, all_items):
                character_manager.save_character(current_character)
        except Exception as e:
            print(f"Item Error: {e}")

def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        try:
            load_game_data()
        except Exception as e:
            print(f"Error loading game data even after creation: {e}")
            return
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    except CorruptedDataError as e:
        print(f"Critical data file corruption: {e}")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()
