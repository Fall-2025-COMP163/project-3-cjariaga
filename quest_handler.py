"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module

Name: Clayan Ariaga

AI Usage: Gemini was used in implementing quest acceptance logic,
prerequisite validation, completion handling, and integration with
character_manager for rewards. This involved quest tracking,
list manipulation, and game state management.

Handles quest acceptance, completion, and prerequisite chains
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)
import character_manager


# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, all_quests):
    """Accept a quest if requirements are met"""
    if quest_id not in all_quests:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")
    
    quest = all_quests[quest_id]
    
    # Check if already completed
    if quest_id in character.get('completed_quests', []):
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed.")
    
    # Check if already active
    if quest_id in character.get('active_quests', []):
        return f"Quest '{quest_id}' already accepted."
    
    # Check level requirement (default to 1 if missing)
    required_level = quest.get('required_level', 1)
    if character.get('level', 0) < required_level:
        raise InsufficientLevelError(
            f"Level {required_level} required (you are level {character.get('level', 0)})"
        )
    
    # Check prerequisites
    prerequisite = quest.get('prerequisite') or 'NONE'
    if prerequisite != 'NONE':
        if prerequisite not in character.get('completed_quests', []):
            raise QuestRequirementsNotMetError(
                f"Must complete '{prerequisite}' first."
            )
    
    # Accept quest
    character.setdefault('active_quests', []).append(quest_id)
    quest_title = quest.get('title', quest_id)
    return f"Accepted quest: {quest_title}"


def complete_quest(character, quest_id, all_quests):
    """Complete a quest and grant rewards"""
    if quest_id not in all_quests:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")
    
    if quest_id not in character.get('active_quests', []):
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")
    
    quest = all_quests[quest_id]
    
    # Remove from active and add to completed
    character['active_quests'].remove(quest_id)
    character.setdefault('completed_quests', []).append(quest_id)
    
    # Grant rewards (default to 0 if missing)
    reward_xp = quest.get('reward_xp', 0)
    reward_gold = quest.get('reward_gold', 0)
    character_manager.gain_experience(character, reward_xp)
    character_manager.add_gold(character, reward_gold)
    
    quest_title = quest.get('title', quest_id)
    return f"Completed: {quest_title} | +{reward_xp} XP, +{reward_gold} gold"


def abandon_quest(character, quest_id):
    """Abandon an active quest"""
    if quest_id not in character.get('active_quests', []):
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")
    
    character['active_quests'].remove(quest_id)
    return f"Abandoned quest: {quest_id}"


# ============================================================================
# QUEST QUERIES
# ============================================================================

def get_active_quests(character, all_quests):
    """Get list of character's active quests"""
    return [all_quests[q_id] for q_id in character.get('active_quests', []) if q_id in all_quests]


def get_completed_quests(character, all_quests):
    """Get list of character's completed quests"""
    return [all_quests[q_id] for q_id in character.get('completed_quests', []) if q_id in all_quests]


def get_available_quests(character, all_quests):
    """Get list of quests character can accept"""
    available = []
    
    for quest_id, quest in all_quests.items():
        # Skip if already active or completed
        if quest_id in character.get('active_quests', []) or quest_id in character.get('completed_quests', []):
            continue
        
        # Check level requirement (default to 1)
        required_level = quest.get('required_level', 1)
        if character.get('level', 0) < required_level:
            continue
        
        # Check prerequisite
        prerequisite = quest.get('prerequisite') or 'NONE'
        if prerequisite != 'NONE' and prerequisite not in character.get('completed_quests', []):
            continue
        
        available.append(quest)
    
    return available


# ============================================================================
# QUEST VALIDATION
# ============================================================================

def validate_quest_prerequisites(all_quests):
    """Validate that quest prerequisites don't have circular dependencies"""
    visited = set()
    rec_stack = set()
    
    def has_cycle(quest_id):
        """Check if quest_id is part of a cycle"""
        if quest_id not in all_quests:
            return False
        
        visited.add(quest_id)
        rec_stack.add(quest_id)
        
        quest = all_quests[quest_id]
        prerequisite = quest.get('prerequisite') or 'NONE'
        
        if prerequisite != 'NONE':
            if prerequisite not in visited:
                if has_cycle(prerequisite):
                    return True
            elif prerequisite in rec_stack:
                return True
        
        rec_stack.remove(quest_id)
        return False
    
    # Check all quests for cycles
    for quest_id in all_quests:
        if quest_id not in visited:
            if has_cycle(quest_id):
                raise ValueError(f"Circular quest dependency detected at: {quest_id}")
    
    return True
