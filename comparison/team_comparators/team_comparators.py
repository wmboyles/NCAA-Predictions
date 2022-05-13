"""
This module contains the TeamComparator abstract base class and its concrete subclasses.
These subclasses compare two teams and give an expected probability of a team winning.
"""


import os
import pickle
from abc import ABC, abstractmethod

import data_scraping
import numpy as np

from ..game_attrs import GameValues, TeamSeeding


class TeamComparator(ABC):
    """
    Interface for comparing two teams based on some ranking.
    Implementing classes can determine what the ranking is based on.
    """

    @abstractmethod
    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        """
        Compare two teams based on some ranking.
        Return a float between 0 and 1 representing the probability that teamA wins.
        """
        ...

    @classmethod
    def get_total_summary(cls, year: int) -> list:
        """
        Helper method for all team comparators to get the total summary of a year.
        """

        try:
            total_summary = pickle.load(
                open(f"./summaries/{year}/total_summary.p", "rb")
            )
        except FileNotFoundError:
            print(
                f"--- WARNING: No summary found for {year}. Trying to create summary..."
            )

            try:
                data_scraping.harvest(year)
            except:
                print(f"--- ERROR: Could not make summary for {year}.")
                return

            print(f"--- SUCCESS: Summary created for {year}")
            print("--- Trying again with newly created summary")

            return cls.get_total_summary(year)

        return total_summary

    @classmethod
    def get_teams(cls, total_summary: list) -> list:
        return list(
            set(
                "-".join(game[GameValues.HOME_TEAM.value].split(" "))
                for game in total_summary
            )
        )

    @classmethod
    def serialize_results(
        cls, year: int, model_name: str, rankings: dict, vec: np.ndarray
    ):
        # Make the year folder
        outfile1 = f"./predictions/{year}_{model_name}_rankings.p"
        outfile2 = f"./predictions/{year}_{model_name}_vector.p"
        os.makedirs(os.path.dirname(outfile1), exist_ok=True)

        pickle.dump(rankings, open(outfile1, "wb"))
        pickle.dump(vec, open(outfile2, "wb"))


class HydridComparator(TeamComparator):
    """
    Uses other TeamComparator models to compare teams.
    The Hybrid model chooses the most confident of the given models to use.
    """

    def __init__(self, *comparators: TeamComparator):
        self.comparators = comparators

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        confs = [
            comparator.compare_teams(teamA, teamB) for comparator in self.comparators
        ]

        min_conf, max_conf = min(confs), max(confs)

        return max_conf if (max_conf >= 1 - min_conf) else min_conf
