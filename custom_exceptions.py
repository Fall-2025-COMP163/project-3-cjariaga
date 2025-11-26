"""
COMP 163 - Project 3: Quest Chronicles
Custom Exception Definitions

This module defines all custom exceptions used throughout the game.
""" 

# ============================================================================
# BASE GAME EXCEPTIONS
# ============================================================================
class GameError(Exception):
    """Base exception for all game-related errors"""
    pass


class DataError(GameError):
    """Base exception for data-related errors"""
    pass


class CharacterError(GameError):
    """Base exception for character-related errors"""
    pass


class CombatError(GameError):
    """Base exception for combat-related errors"""
    pass


class QuestError(GameError):
    """Base exception for quest-related errors"""
    pass


class InventoryError(GameError):
    """Base exception for inventory-related errors"""
    pass


# ============================================================================
# SPECIFIC EXCEPTIONS
# ============================================================================
# Data Loading Exceptions
class InvalidDataFormatError(DataError):
    """Raised when data file has incorrect format"""
    pass


class MissingDataFileError(DataError):
    """Raised when required data file is not found"""
    pass


class CorruptedDataError(DataError):
    """Raised when data file is corrupted or unreadable"""
    pass


# Character Exceptions
class InvalidCharacterClassError(CharacterError):
    """Raised when an invalid character class is chosen"""
    pass


class CharacterNotFoundError(CharacterError):
    """Raised when a save file for the character is not found"""
    pass


class InsufficientLevelError(CharacterError):
    """Raised when a character's level is too low for an action"""
    pass


class CharacterDeadError(CharacterError):
    """Raised when a character is dead and attempts an action"""
    pass


# Combat Exceptions
class InvalidTargetError(CombatError):
    """Raised when a target is not a valid enemy"""
    pass


class CombatNotActiveError(CombatError):
    """Raised when trying to perform combat actions outside of battle"""
    pass


class AbilityOnCooldownError(CombatError):
    """Raised when trying to use an ability that's on cooldown"""
    pass


# Quest Exceptions
class QuestNotFoundError(QuestError):
    """Raised when trying to access a quest that doesn't exist"""
    pass


class QuestRequirementsNotMetError(QuestError):
    """Raised when trying to start a quest without meeting requirements"""
    pass


class QuestAlreadyCompletedError(QuestError):
    """Raised when trying to accept an already completed quest"""
    pass


class QuestNotActiveError(QuestError):
    """Raised when trying to complete a quest that isn't active"""
    pass


# Inventory Exceptions
class InventoryFullError(InventoryError):
    """Raised when trying to add items to a full inventory"""
    pass


class ItemNotFoundError(InventoryError):
    """Raised when trying to use an item that doesn't exist"""
    pass


class InsufficientResourcesError(InventoryError):
    """Raised when player doesn't have enough gold or items"""
    pass


class InvalidItemTypeError(InventoryError):
    """Raised when item type is not recognized"""
    pass


# Save/Load Exceptions
class SaveFileCorruptedError(GameError):
    """Raised when save file cannot be loaded due to corruption"""
    pass


class InvalidSaveDataError(GameError):
    """Raised when save file contains invalid data"""
    pass


# Expose names for predictable import behavior
__all__ = [
    "GameError", "DataError", "CharacterError", "CombatError", "QuestError", "InventoryError",
    "InvalidDataFormatError", "MissingDataFileError", "CorruptedDataError",
    "InvalidCharacterClassError", "CharacterNotFoundError", "InsufficientLevelError",
    "CharacterDeadError",
    "InvalidTargetError", "CombatNotActiveError", "AbilityOnCooldownError",
    "QuestNotFoundError", "QuestRequirementsNotMetError", "QuestAlreadyCompletedError",
    "QuestNotActiveError",
    "InventoryFullError", "ItemNotFoundError", "InsufficientResourcesError", "InvalidItemTypeError",
    "SaveFileCorruptedError", "InvalidSaveDataError"
]
