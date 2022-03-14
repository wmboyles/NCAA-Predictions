"""
This module contains enums that represent attributes of a game and their relative weights.
It also contains a class to represent the state of a team within a tournament.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass
class TeamSeeding:
    name: str
    seed: int
    probability: float


class GameValues(Enum):
    """
    Items in this enum are the different indexes of the "four factor" statistics
    that the cleaner program extracts and calculates for each game.
    To use their value, you'd write game[GameValue.ITEM.value]

    In all instances, a high value of game[GameValue.ITEM.value] means a better team
    """

    HOME_TEAM = 0  # Name of first (called home but not always) team
    AWAY_TEAM = 1  # Name of second (called away but not always) team

    WIN_LOSS = 2  # Did the home/first team win?

    HOME_SCORE = 3  # The home/first team's score
    AWAY_SCORE = 4  # The away/second team's score

    HOME_eFGp = 5  # The home/first team's effective field goal percentage
    AWAY_eFGp = 6  # The away/second team's effective field goal percentage

    HOME_TOVp = 7  # The home/first team's turnover percentage
    AWAY_TOVp = 8  # The away/second team's turnover percentage

    HOME_ORBp = 9  # The home/first team's offensive rebound percentage
    AWAY_ORBp = 10  # The away/second team's offensive rebound percentage

    HOME_FTR = 11  # The home/first team's free throw rate
    AWAY_FTR = 12  # The away/second team's free throw rate


class GameWeights(Enum):
    """
    Items in this enum are the weights of a team winning game and the "four factors":
        * Effective field goal percentage
        * Turnover percentage
        * Offensive rebound percentage
        * Free throw rate.
    These weights can be changed to change the importance of these factors in each game.
    """

    WEIGHTS = [50, 13.3333, 6.6666, 8.3333, 5]
