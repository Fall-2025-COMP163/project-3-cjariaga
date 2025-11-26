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

    key = enemy_type.lower()
    if key not in enemies:
        raise InvalidTargetError(f"Unknown enemy: {enemy_type}")

    # Return a shallow copy so callers can mutate safely
    return dict(enemies[key])


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
        # Expect character and enemy as dict-like objects
        self.character = character
        self.enemy = enemy
        self.combat_active = False
        self.turn = 0
        self.ability_cooldown = 0
        self.battle_log = []

    def start_battle(self):
        """Start the combat loop. Returns a summary dict when battle ends."""
        if character_manager.is_character_dead(self.character):
            raise CharacterDeadError("Cannot start battle while dead")

        self.combat_active = True
        self.battle_log.append(f"A wild {self.enemy.get('name', 'Enemy')} appears!")

        while self.combat_active:
            self.turn += 1
            self.battle_log.append(f"--- Turn {self.turn} ---")

            # reduce cooldown at start of turn (so new ability sets 2 -> next turn 1 -> etc.)
            if self.ability_cooldown > 0:
                self.ability_cooldown -= 1

            try:
                # For interactive runs, player_turn will prompt; for tests you can call player_turn(choice=...)
                self.player_turn()
            except CombatNotActiveError:
                # Player escaped
                self.battle_log.append("Player escaped.")
                break

            if self.check_battle_end():
                break

            self.enemy_turn()

            if self.check_battle_end():
                break

        # Ensure health floors at 0
        self.enemy['health'] = max(0, self.enemy.get('health', 0))
        self.character['health'] = max(0, self.character.get('health', 0))
        self.combat_active = False

        # Determine result
        if self.enemy['health'] <= 0 and self.character['health'] > 0:
            rewards = get_victory_rewards(self.enemy)
            character_manager.gain_experience(self.character, rewards['xp'])
            character_manager.add_gold(self.character, rewards['gold'])
            self.battle_log.append(f"Victory! Gained {rewards['xp']} XP and {rewards['gold']} gold.")
            return {'winner': 'player', 'xp_gained': rewards['xp'], 'gold_gained': rewards['gold']}
        elif self.character['health'] <= 0:
            self.battle_log.append("Defeated by enemy.")
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}
        else:
            return {'winner': 'none', 'xp_gained': 0, 'gold_gained': 0}

    def player_turn(self, choice=None):
        """
        Handle player's turn.
        - choice: optional string '1'|'2'|'3' so callers/tests can be non-interactive.
        If choice is None the function will prompt via input() (preserves interactive behavior).
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat not active")

        if choice is None:
            # Keep interactive behavior for manual runs
            print("\n1. Attack  2. Special  3. Run")
            choice = input("Choice: ").strip()
        else:
            choice = str(choice).strip()

        if choice == '1':
            damage = self.calculate_damage(self.character, self.enemy)
            self.enemy['health'] = max(0, self.enemy.get('health', 0) - damage)
            msg = f"You deal {damage} damage!"
            self.battle_log.append(msg)
            print(msg)
        elif choice == '2':
            if self.ability_cooldown > 0:
                # Keep raising so tests can assert cooldown behavior if desired
                raise AbilityOnCooldownError(f"Cooldown: {self.ability_cooldown} turns")
            msg = use_special_ability(self.character, self.enemy)
            # Some abilities (Cleric heal) return amounts; ensure proper logging
            self.ability_cooldown = 2
            self.battle_log.append(msg)
            print(msg)
        elif choice == '3':
            # 50% chance to escape
            if random.random() < 0.5:
                self.combat_active = False
                raise CombatNotActiveError("Escaped")
            else:
                msg = "Failed to escape!"
                self.battle_log.append(msg)
                print(msg)
        else:
            # Invalid choice results in no action but is logged
            msg = "Invalid action."
            self.battle_log.append(msg)
            print(msg)

    def enemy_turn(self):
        """Handle enemy's turn"""
        if not self.combat_active:
            raise CombatNotActiveError("Combat not active")

        damage = self.calculate_damage(self.enemy, self.character)
        self.character['health'] = max(0, self.character.get('health', 0) - damage)
        msg = f"{self.enemy.get('name','Enemy')} deals {damage} damage!"
        self.battle_log.append(msg)
        print(msg)

    def calculate_damage(self, attacker, defender):
        """Calculate damage from attacker to defender (simple formula)."""
        # Default stats if missing
        attack_stat = int(attacker.get('strength', 5))
        # If attacker is a spellcaster, prioritize magic
        if attacker.get('class') == 'Mage' or attacker.get('magic', 0) > attacker.get('strength', 0):
            attack_stat = int(attacker.get('magic', 5))

        # Base damage at least 1
        base = max(1, attack_stat)
        low = max(1, int(base * 0.8))
        high = max(low, int(base * 1.2))
        damage = random.randint(low, high)
        return damage

    def check_battle_end(self):
        """Return True if either side has 0 or less HP."""
        if self.enemy.get('health', 0) <= 0:
            return True
        if self.character.get('health', 0) <= 0:
            return True
        return False


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================
def use_special_ability(character, enemy):
    """Use character's class-specific special ability."""
    char_class = character.get('class', '')

    if char_class == 'Warrior':
        damage = max(1, int(character.get('strength', 1)) * 2)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))
        enemy['health'] = max(0, enemy.get('health', 0) - damage)
        return f"Power Strike! {damage} damage!"

    elif char_class == 'Mage':
        damage = max(1, int(character.get('magic', 1)) * 2)
        damage = random.randint(int(damage * 0.8), int(damage * 1.2))
        enemy['health'] = max(0, enemy.get('health', 0) - damage)
        return f"Fireball! {damage} damage!"

    elif char_class == 'Rogue':
        if random.random() < 0.5:
            damage = max(1, int(character.get('strength', 1)) * 3)
            damage = random.randint(int(damage * 0.8), int(damage * 1.2))
            enemy['health'] = max(0, enemy.get('health', 0) - damage)
            return f"CRITICAL STRIKE! {damage} damage!"
        else:
            damage = max(1, int(character.get('strength', 1)))
            enemy['health'] = max(0, enemy.get('health', 0) - damage)
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
    return {'xp': int(enemy.get('xp_reward', 0)), 'gold': int(enemy.get('gold_reward', 0))}


def display_combat_stats(character, enemy):
    """Display current combat status (safe access)."""
    c_name = character.get('name', 'Player')
    e_name = enemy.get('name', 'Enemy')
    c_health = f"{character.get('health', 0)}/{character.get('max_health', 0)}"
    e_health = f"{enemy.get('health', 0)}/{enemy.get('max_health', 0)}"
    print(f"  {c_name}: {c_health} HP")
    print(f"  {e_name}: {e_health} HP")
