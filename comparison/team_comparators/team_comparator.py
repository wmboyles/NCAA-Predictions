import os
import pickle
import numpy as np
from abc import ABC, abstractmethod

import data_scraping
from ..game_attrs import GameValues, Team


class TeamComparator(ABC):
    """
    Interface for comparing two teams based on some ranking.
    Implementing classes can determine what the ranking is based on.

    The only requirements for a comparator model are:

    1. Initialization of the comparator can only require the current year as input.
       All other parameters must be optional.
    2. Implement the `compare_teams` method, which takes two teams, A and B,
       and returns the probability of A beating B.
    """

    def __init__(self, year: int, gender: str):
        print(f"--- Initializing {self.__class__.__name__} {gender} for {year} ---")

    @abstractmethod
    def compare_teams(self, teamA: Team, teamB: Team) -> float:
        """
        Compare two teams based on some ranking.
        Return a float between 0 and 1 representing the probability that teamA wins.
        """
        ...

    @classmethod
    def get_total_summary(cls, year: int, gender: str) -> list:
        """
        Helper method for all team comparators to get the total summary of a year.
        """

        try:
            total_summary = pickle.load(
                open(f"./summaries/{gender}/{year}/total_summary.p", "rb")
            )
        except FileNotFoundError:
            print(
                f"--- WARNING: No summary found for {gender} {year}. Trying to create summary..."
            )

            try:
                data_scraping.harvest(year, gender)
            except:
                print(f"--- ERROR: Could not make summary for {gender} {year}.")
                return

            print(f"--- SUCCESS: Summary created for {gender} {year}")
            print("--- Trying again with newly created summary")

            return cls.get_total_summary(year, gender)

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
        cls, year: int, model_name: str, rankings: dict, vec: np.ndarray, gender: str
    ):
        # Make the year folder
        outfile1 = f"./predictions/{gender}/{year}_{model_name}_rankings.p"
        outfile2 = f"./predictions/{gender}/{year}_{model_name}_vector.p"
        os.makedirs(os.path.dirname(outfile1), exist_ok=True)

        if rankings is not None:
            pickle.dump(rankings, open(outfile1, "wb"))
        if vec is not None:
            pickle.dump(vec, open(outfile2, "wb"))


class HydridComparator(TeamComparator):
    """
    Uses other TeamComparator models to compare teams.
    The Hybrid model chooses the most confident of the given models to use.
    """

    def __init__(self, *comparators: TeamComparator):
        self.comparators = comparators

    def compare_teams(self, teamA: Team, teamB: Team) -> float:
        confs = [
            comparator.compare_teams(teamA, teamB) for comparator in self.comparators
        ]
        min_conf, max_conf = min(confs), max(confs)

        return max_conf if (max_conf >= 1 - min_conf) else min_conf
