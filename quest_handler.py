"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles quest management, dependencies, and completion.
"""

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

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest.

    Returns: True if quest accepted
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        InsufficientLevelError if character level too low
        QuestRequirementsNotMetError if prerequisite not completed
        QuestAlreadyCompletedError if quest already done
    """
    quest = quest_data_dict.get(quest_id)

    if not quest:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' does not exist.")

    # 1. Check if quest is already completed
    if quest_id in character['completed_quests']:
        raise QuestAlreadyCompletedError(f"Quest '{quest['TITLE']}' has already been completed.")

    # 2. Check if quest is already active
    if quest_id in character['active_quests']:
        print(f"Quest '{quest['TITLE']}' is already active.")
        return False  # Not an error, just prevents re-adding

    # 3. Check level requirement
    required_level = quest['REQUIRED_LEVEL']
    if character['level'] < required_level:
        raise InsufficientLevelError(f"Level {required_level} required. You are only Level {character['level']}.")

    # 4. Check prerequisite
    prereq_id = quest['PREREQUISITE']
    if prereq_id != 'NONE':
        if prereq_id not in character['completed_quests']:
            # For better UX, get the title of the prerequisite quest
            prereq_title = quest_data_dict.get(prereq_id, {}).get('TITLE', prereq_id)
            raise QuestRequirementsNotMetError(f"Prerequisite quest '{prereq_title}' must be completed first.")

    # Success: Add to active quests
    character['active_quests'].append(quest_id)
    print(f"\n✅ Quest Accepted: {quest['TITLE']}")
    print(f"   Description: {quest['DESCRIPTION']}")
    print(f"   Rewards: {quest['REWARD_XP']} XP, {quest['REWARD_GOLD']} Gold")
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Mark an active quest as complete and apply rewards.

    NOTE: The main game loop must handle the quest objective (e.g., defeating enemies).
          This function handles the reward process.

    Returns: Dictionary with {'xp': X, 'gold': Y} rewards.
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        QuestNotActiveError if quest is not currently active
    """
    quest = quest_data_dict.get(quest_id)

    if not quest:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' does not exist.")

    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest '{quest['TITLE']}' is not currently active.")

    # Apply rewards
    xp_reward = quest['REWARD_XP']
    gold_reward = quest['REWARD_GOLD']

    character['experience'] += xp_reward
    character['gold'] += gold_reward

    # Update quest lists
    character['active_quests'].remove(quest_id)
    character['completed_quests'].append(quest_id)

    print("\nQUEST COMPLETE! ---------------------")
    print(f"🏆 {quest['TITLE']} Completed!")
    print(f"   Gained: {xp_reward} XP, {gold_reward} Gold.")
    print("-------------------------------------")

    return {'xp': xp_reward, 'gold': gold_reward}


def check_prerequisites(character, quest_id, quest_data_dict):
    """
    Check if a character meets the level and prerequisite quest requirements.

    Returns: Tuple (bool meets_req, str message)
    """
    quest = quest_data_dict.get(quest_id)
    if not quest:
        return (False, "Quest not found.")

    # Check level
    required_level = quest['REQUIRED_LEVEL']
    if character['level'] < required_level:
        return (False, f"Requires Level {required_level}.")

    # Check prerequisite
    prereq_id = quest['PREREQUISITE']
    if prereq_id != 'NONE':
        if prereq_id not in character['completed_quests']:
            prereq_title = quest_data_dict.get(prereq_id, {}).get('TITLE', prereq_id)
            return (False, f"Requires completion of '{prereq_title}'.")

    # Check if already complete/active
    if quest_id in character['completed_quests']:
        return (False, "Already Completed.")
    if quest_id in character['active_quests']:
        return (False, "Already Active.")

    return (True, "Ready to accept.")


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist.

    Returns: True if all valid
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    for quest_id, quest in quest_data_dict.items():
        prereq_id = quest.get('PREREQUISITE')
        if prereq_id and prereq_id != 'NONE':
            if prereq_id not in quest_data_dict:
                raise QuestNotFoundError(
                    f"Quest '{quest_id}' has an invalid prerequisite ID: '{prereq_id}'. "
                    "The prerequisite quest does not exist."
                )
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    from game_data import load_quests, create_default_data_files

    print("=== QUEST HANDLER TEST ===")

    # Setup data
    create_default_data_files()
    test_quests = load_quests()

    # Test character
    test_char = {
        'level': 1,
        'active_quests': [],
        'completed_quests': [],
        'experience': 0,
        'gold': 100
    }

    # 1. Test data validation
    try:
        validate_quest_prerequisites(test_quests)
        print("Prerequisite validation successful.")
    except QuestNotFoundError as e:
        print(f"Prerequisite validation FAILED: {e}")

    # 2. Test accepting the first quest
    try:
        accept_quest(test_char, 'tutorial_1', test_quests)
        print(f"Active Quests: {test_char['active_quests']}")
    except Exception as e:
        print(f"Accept quest error: {e}")

    # 3. Test accepting second quest (prerequisite not met)
    try:
        accept_quest(test_char, 'warrior_path', test_quests)
    except QuestRequirementsNotMetError as e:
        print(f"Successfully caught prereq not met: {e}")

    # 4. Test completing the first quest
    try:
        rewards = complete_quest(test_char, 'tutorial_1', test_quests)
        print(f"New XP: {test_char['experience']}, New Gold: {test_char['gold']}")
        print(f"Completed Quests: {test_char['completed_quests']}")
    except Exception as e:
        print(f"Complete quest error: {e}")

    # 5. Test accepting second quest (should now succeed if level is met)
    test_char['level'] = 3  # Manually increase level to pass level check
    try:
        accept_quest(test_char, 'warrior_path', test_quests)
        print("Warrior path quest accepted after completing prerequisite.")
    except Exception as e:
        print(f"Accept quest error: {e}")
