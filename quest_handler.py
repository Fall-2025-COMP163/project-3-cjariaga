"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: Clayan Ariaga

AI Usage: Gemini, was used to help implementing
quest logic by checking prerequisites, levels, and completion status.
It also required integrating with the character_manager module to
grant rewards, demonstrating cross-module interaction.

This module handles quest management, dependencies, and completion.
"""
import character_manager
from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)


# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data):
    """Accept a new quest"""
    if quest_id not in quest_data:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    quest = quest_data[quest_id]

    if quest_id in character['completed_quests']:
        raise QuestAlreadyCompletedError(f"Quest already completed.")

    if quest_id in character['active_quests']:
        raise QuestAlreadyCompletedError(f"Quest already active.")

    if character['level'] < quest['required_level']:
        raise InsufficientLevelError(f"Need level {quest['required_level']}.")

    if quest['prerequisite'] != 'NONE' and quest['prerequisite'] not in character['completed_quests']:
        raise QuestRequirementsNotMetError(f"Need to complete '{quest['prerequisite']}' first.")

    character['active_quests'].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data):
    """Complete an active quest and grant rewards"""
    if quest_id not in quest_data:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")

    quest = quest_data[quest_id]

    character['active_quests'].remove(quest_id)
    character['completed_quests'].append(quest_id)

    character_manager.gain_experience(character, quest['reward_xp'])
    character_manager.add_gold(character, quest['reward_gold'])

    return {'xp': quest['reward_xp'], 'gold': quest['reward_gold']}


def abandon_quest(character, quest_id):
    """Remove quest from active quests"""
    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")
    character['active_quests'].remove(quest_id)
    return True


def get_active_quests(character, quest_data):
    """Get all active quests"""
    return [quest_data[qid] for qid in character['active_quests'] if qid in quest_data]


def get_completed_quests(character, quest_data):
    """Get all completed quests"""
    return [quest_data[qid] for qid in character['completed_quests'] if qid in quest_data]


def get_available_quests(character, quest_data):
    """Get quests that can be accepted"""
    available = []
    for qid, quest in quest_data.items():
        if qid in character['completed_quests'] or qid in character['active_quests']:
            continue
        if character['level'] < quest['required_level']:
            continue
        if quest['prerequisite'] != 'NONE' and quest['prerequisite'] not in character['completed_quests']:
            continue
        available.append(quest)
    return available


# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """Check if quest is completed"""
    return quest_id in character['completed_quests']


def is_quest_active(character, quest_id):
    """Check if quest is active"""
    return quest_id in character['active_quests']


def can_accept_quest(character, quest_id, quest_data, raise_exceptions=False):
    """Check if character can accept quest"""
    try:
        if quest_id not in quest_data:
            raise QuestNotFoundError("Quest not found")
        if quest_id in character['completed_quests']:
            raise QuestAlreadyCompletedError("Already completed")
        if quest_id in character['active_quests']:
            raise QuestAlreadyCompletedError("Already active")

        quest = quest_data[quest_id]
        if character['level'] < quest['required_level']:
            raise InsufficientLevelError("Level too low")
        if quest['prerequisite'] != 'NONE' and quest['prerequisite'] not in character['completed_quests']:
            raise QuestRequirementsNotMetError("Prerequisite not met")

        return True, "Can accept"
    except Exception as e:
        if raise_exceptions:
            raise
        return False, str(e)


# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data):
    """Calculate completion percentage"""
    if not quest_data:
        return 100.0
    return (len(character['completed_quests']) / len(quest_data)) * 100


def get_total_quest_rewards_earned(character, quest_data):
    """Calculate total rewards from completed quests"""
    total_xp = 0
    total_gold = 0
    for qid in character['completed_quests']:
        if qid in quest_data:
            total_xp += quest_data[qid]['reward_xp']
            total_gold += quest_data[qid]['reward_gold']
    return {'total_xp': total_xp, 'total_gold': total_gold}


# ============================================================================
# DISPLAY
# ============================================================================

def display_quest_list(quests, quest_data):
    """Display list of quests"""
    if not quests:
        print("  No quests.")
        return
    for q in quests:
        print(f"  [{q['quest_id']}] {q['title']} (Lv {q['required_level']})")


def display_character_quest_progress(character, quest_data):
    """Display quest progress"""
    print(f"\nActive: {len(character['active_quests'])}")
    print(f"Completed: {len(character['completed_quests'])}")
    print(f"Progress: {get_quest_completion_percentage(character, quest_data):.1f}%")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data):
    """Validate all quest prerequisites exist"""
    for qid, quest in quest_data.items():
        prereq = quest['prerequisite']
        if prereq != 'NONE' and prereq not in quest_data:
            raise QuestNotFoundError(f"Quest '{qid}' has invalid prerequisite '{prereq}'")
    return True
