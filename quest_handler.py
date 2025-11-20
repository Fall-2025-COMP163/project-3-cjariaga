"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: Clayan Ariaga

AI Usage: Gemini in implemanting turn-based logic, damage formulas,
and class-specific special abilities. It also required integration
with character_manager for healing and stat checks.

Handles combat mechanics
"""

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)
import character_manager


# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """Create an enemy based on type"""
    enemies = {
        "goblin": {'name': 'Goblin', 'health': 50, 'max_health': 50,
                   'strength': 8, 'magic': 2, 'xp_reward': 25, 'gold_reward': 10},
        "orc": {'name': 'Orc', 'health': 80, 'max_health': 80,
                'strength': 12, 'magic': 5, 'xp_reward': 50, 'gold_reward': 25},
        "dragon": {'name': 'Dragon', 'health': 200, 'max_health': 200,
                   'strength': 25, 'magic': 15, 'xp_reward': 200, 'gold_reward': 100}
    }

    if enemy_type.lower() not in enemies:
        raise InvalidTargetError(f"Unknown enemy: {enemy_type}")

    return enemies[enemy_type.lower()]


def get_random_enemy_for_level(character_level):
    """Get appropriate enemy for character's level"""
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """Simple turn-based combat system"""

    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
        self.combat_active = False
        self.turn = 0
        self.ability_cooldown = 0
        self.battle_log = []

    def start_battle(self):
        """Start the combat loop"""
        if character_manager.is_character_dead(self.character):
            raise CharacterDeadError("Cannot start battle while dead")

        self.combat_active = True
        print(f"\nA wild {self.enemy['name']} appears!")

        while self.combat_active:
            self.turn += 1
            print(f"\n--- Turn {self.turn} ---")
            display_combat_stats(self.character, self.enemy)

            if self.ability_cooldown > 0:
                self.ability_cooldown -= 1

            try:
                self.player_turn()
            except CombatNotActiveError:
                print("You escaped!")
                break

            if self.check_battle_end():
                break

            self.enemy_turn()

            if self.check_battle_end():
                break

        self.combat_active = False

        if self.enemy['health'] <= 0:
            print(f"You defeated the {self.enemy['name']}!")
            rewards = get_victory_rewards(self.enemy)
            character_manager.gain_experience(self.character, rewards['xp'])
            character_manager.add_gold(self.character, rewards['gold'])
            return {'winner': 'player', 'xp_gained': rewards['xp'], 'gold_gained': rewards['gold']}
        elif self.character['health'] <= 0:
            print("You were defeated...")
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}
        else:
            return {'winner': 'none', 'xp_gained': 0, 'gold_gained': 0}

    def player_turn(self):
        """Handle player's turn"""
        if not self.combat_active:
            raise CombatNotActiveError("Combat not active")

        print("\n1. Attack  2. Special  3. Run")
        choice = input("Choice: ").strip()

        if choice == '1':
            damage = self.calculate_damage(self.character, self.enemy)
            self.enemy['health'] -= damage
            print(f"You deal {damage} damage!")
        elif choice == '2':
            if self.ability_cooldown > 0:
                raise AbilityOnCooldownError(f"Cooldown: {self.ability_cooldown} turns")
            msg = use_special_ability(self.character, self.enemy)
            print(msg)
            self.ability_cooldown = 2
        elif choice == '3':
            if random.random() < 0.5:
                self.combat_active = False
                raise CombatNotActiveError("Escaped")
            else:
                print("Failed to escape!")

    def enemy_turn(self):
        """Handle enemy's turn"""
        if not self.combat_active:
            raise CombatNotActiveError("Combat not active")

        damage = self.calculate_damage(self.enemy, self.character)
        self.character['health'] -= damage
        print(f"{self.enemy['name']} deals {damage} damage!")

    def calculate_damage(self, attacker, defender):
        """Calculate damage from attack"""
        attack_stat = attacker.get('strength', 5)

        if attacker.get('class') == 'Mage' or attacker.get('magic', 0) > attacker.get('strength', 0):
            attack_stat = attacker.get('magic', 5)

        damage = max(1, attack_stat)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))
        return damage

    def check_battle_end(self):
        """Check if battle is over"""
        if self.enemy['health'] <= 0:
            return True
        if self.character['health'] <= 0:
            return True
        return False


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """Use character's class-specific special ability"""
    char_class = character['class']

    if char_class == 'Warrior':
        damage = max(1, character['strength'] * 2)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))
        enemy['health'] -= damage
        return f"Power Strike! {damage} damage!"

    elif char_class == 'Mage':
        damage = max(1, character['magic'] * 2)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))
        enemy['health'] -= damage
        return f"Fireball! {damage} damage!"

    elif char_class == 'Rogue':
        if random.random() < 0.5:
            damage = max(1, character['strength'] * 3)
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
            enemy['health'] -= damage
            return f"CRITICAL STRIKE! {damage} damage!"
        else:
            damage = max(1, character['strength'])
            enemy['health'] -= damage
            return f"Missed critical. {damage} damage."

    elif char_class == 'Cleric':
        healed = character_manager.heal_character(character, 30)
        return f"Heal! Restored {healed} HP."

    return "No special ability."


# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """Check if character can fight"""
    return not character_manager.is_character_dead(character)


def get_victory_rewards(enemy):
    """Calculate rewards for defeating enemy"""
    return {'xp': enemy['xp_reward'], 'gold': enemy['gold_reward']}


def display_combat_stats(character, enemy):
    """Display current combat status"""
    print(f"  {character['name']}: {character['health']}/{character['max_health']} HP")
    print(f"  {enemy['name']}: {enemy['health']}/{enemy['max_health']} HP")
