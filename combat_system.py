"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: Clayan Ariaga

AI Usage: [Document any AI assistance used]

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

ENEMY_STATS = {
    'goblin': {'name': 'Goblin', 'health': 50, 'strength': 8, 'magic': 2, 'xp_reward': 25, 'gold_reward': 10},
    'orc':    {'name': 'Orc',    'health': 80, 'strength': 12, 'magic': 5, 'xp_reward': 50, 'gold_reward': 25},
    'dragon': {'name': 'Dragon', 'health': 200, 'strength': 25, 'magic': 15, 'xp_reward': 200, 'gold_reward': 100}
}

def create_enemy(enemy_type):
    """
    Create an enemy based on type.
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_base = ENEMY_STATS.get(enemy_type.lower())
    if not enemy_base:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized.")
        
    # Create a copy so we don't modify the base stats
    enemy = enemy_base.copy()
    enemy['max_health'] = enemy['health']
    # Add an ID for tracking/dialogue purposes, though not strictly required
    enemy['id'] = enemy_type.lower()
    
    return enemy

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level.
    
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    
    Returns: Enemy dictionary
    """
    if character_level >= 6:
        enemy_type = 'dragon'
    elif character_level >= 3:
        enemy_type = 'orc'
    else:
        enemy_type = 'goblin'
        
    return create_enemy(enemy_type)

# ============================================================================
# COMBAT MECHANICS
# ============================================================================

class SimpleBattle:
    """Represents a simple turn-based battle between a character and an enemy."""
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
        self.is_active = True
        display_battle_log(f"A wild {enemy['name']} appears!")

    def attack(self):
        """Perform a standard physical attack."""
        if not self.is_active:
            raise CombatNotActiveError("Cannot attack: Combat is not active.")
        
        # Player Turn (using Strength stat)
        player_damage = calculate_damage(self.character['strength'], self.enemy['name'])
        self.enemy['health'] -= player_damage
        display_battle_log(f"You strike the {self.enemy['name']} for {player_damage} damage!")

        # Check for enemy death
        if self.enemy['health'] <= 0:
            self.enemy['health'] = 0
            display_battle_log(f"The {self.enemy['name']} has been defeated!")
            self.is_active = False
            return True # Battle ended

        # Enemy Turn (using Strength stat)
        enemy_damage = calculate_damage(self.enemy['strength'], self.character['name'])
        self.character['health'] -= enemy_damage
        display_battle_log(f"The {self.enemy['name']} attacks you for {enemy_damage} damage!")

        # Check for character death
        if self.character['health'] <= 0:
            self.character['health'] = 0
            display_battle_log(f"You have been defeated by the {self.enemy['name']}!")
            self.is_active = False
            # Does not return True, as only the player can win for rewards
            
        return self.character['health'] > 0 and self.enemy['health'] > 0 # Battle still active

    def run(self):
        """Attempt to flee combat."""
        if not self.is_active:
            raise CombatNotActiveError("Cannot run: Combat is not active.")
        
        # Simple 50/50 chance to run
        if random.choice([True, False]):
            self.is_active = False
            display_battle_log("You successfully escaped!")
            return True
        else:
            display_battle_log("You failed to escape! The enemy attacks!")
            
            # Enemy attack on failed run
            enemy_damage = calculate_damage(self.enemy['strength'], self.character['name'])
            self.character['health'] -= enemy_damage
            display_battle_log(f"The {self.enemy['name']} attacks you for {enemy_damage} damage!")
            
            if self.character['health'] <= 0:
                self.character['health'] = 0
                display_battle_log(f"You have been defeated by the {self.enemy['name']}!")
                self.is_active = False
                raise CharacterDeadError("Your character died while trying to run!")
                
            return False

def calculate_damage(attacker_stat, target_name):
    """
    Calculate damage based on a stat (Strength or Magic).
    
    Includes a small random variance (e.g., +/- 10%)
    """
    base_damage = attacker_stat * 1.5
    variance = base_damage * 0.1 # 10% variance
    damage = int(random.uniform(base_damage - variance, base_damage + variance))
    
    # Damage cannot be less than 1
    return max(1, damage)

def calculate_rewards(enemy):
    """
    Calculate XP and Gold rewards from a defeated enemy.
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    # Simple calculation: rewards are based on the enemy's definition
    # A small random bonus is added for flavor (up to 20%)
    xp = enemy['xp_reward'] + random.randint(0, int(enemy['xp_reward'] * 0.2))
    gold = enemy['gold_reward'] + random.randint(0, int(enemy['gold_reward'] * 0.2))
    
    return {'xp': xp, 'gold': gold}

def display_combat_stats(character, enemy):
    """
    Display current combat status.
    
    Shows both character and enemy health/stats
    """
    print("----------------------------------------")
    print(f"⚔️ {character['name']} (Lvl {character['level']})")
    print(f"   HP: {character['health']}/{character['max_health']}")
    print(f"   STR: {character['strength']} | MAG: {character['magic']}")
    print()
    print(f"👹 {enemy['name']}")
    print(f"   HP: {enemy['health']}/{enemy['max_health']}")
    print(f"   STR: {enemy['strength']} | MAG: {enemy['magic']}")
    print("----------------------------------------")

def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    try:
        goblin = create_enemy("goblin")
        print(f"Created {goblin['name']}")
    except InvalidTargetError as e:
        print(f"Invalid enemy: {e}")
    
    # Test battle setup
    test_char = {
        'name': 'Hero',
        'class': 'Warrior',
        'level': 1,
        'health': 120,
        'max_health': 120,
        'strength': 15,
        'magic': 5
    }
    
    goblin = create_enemy("goblin")
    battle = SimpleBattle(test_char, goblin)
    
    # Test battle loop until one is defeated or 3 rounds pass
    for i in range(3):
        if not battle.is_active:
            break
        
        print(f"\n--- ROUND {i+1} ---")
        display_combat_stats(test_char, battle.enemy)
        
        try:
            battle.attack()
        except CharacterDeadError as e:
            print(f"Game Over: {e}")
            break
            
    if not battle.is_active:
        if test_char['health'] > 0:
            rewards = calculate_rewards(battle.enemy)
            print(f"VICTORY! Gained {rewards['xp']} XP and {rewards['gold']} Gold.")
        else:
            print("DEFEAT!")
