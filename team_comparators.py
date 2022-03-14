import os
import pickle
from math import sqrt

import matplotlib
import numpy as np
from scipy.stats import chi2

import data_scraping

matplotlib.use("TkAgg")
from abc import ABC, abstractmethod
from enum import Enum

import matplotlib.pyplot as plt


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


class TeamComparator(ABC):
    @abstractmethod
    def compare_teams(self, teamA, teamB) -> float:
        ...


class PageRankComparator(TeamComparator):
    """
    Ranks all Division I NCAA Basketball teams in a given year using PageRank.

    PARAMETERS
    year -->    The year that the NCAA championship game takes place.
                The 2019-2020 season would correpond to year=2020.
    alpha -->   A value between 0 and 1 that is a measure of randomness in
                PageRank meant to model the possibility that a user randomly
                navigates to a page without using a link. alpha=1 would be
                completely deterministic, while alpha=0 would be completely
                random. Google is rumored to use alpha=.85.
    iters -->   The number of iterations of PageRank matrix multiplication to
                perform. The default of iters=3500, about 10x the number of
                Division I teams, is generally sufficient for ranking.
    """

    def __init__(self, year: int, alpha: float = 0.85, iters: int = 10000):
        self.year = year
        self.alpha = alpha
        self.iters = iters

        # Build PageRank stuff
        self.__rank(serialize_results=True, first_year=True)
        self.__build_model()

    def __rank(self, **kwargs: dict[str, bool]):
        """
        Uses PageRank to create a vector ranking all teams.

        KWARGS
        print_rankings -->  Should the function print out its rankings to stdout?
                            Defaults to False.
        plot_rankings -->   Should the function plot the rankings in sorted order?
                            Defaults to False.
        serialize_results -->   Should the function save its rankings to a .p file
                                called "./predictions/[YEAR]/rankings.p"?
                                Defaults to True.
        """

        # Try to deserialize .p file summary. Try to create it if it doesn't exist
        try:
            total_summary = pickle.load(
                open(f"./summaries/{self.year}/total_summary.p", "rb")
            )
        except FileNotFoundError:
            print(
                f"--- WARNING: No summary found for {self.year} Trying to create summary..."
            )
            try:
                data_scraping.harvest(self.year)
            except:
                print(f"--- ERROR: Could not make summary for {self.year}")
                return

            print(f"--- SUCCESS: Summary created for {self.year}")
            print("--- Trying to rank again with newly created summary")

            self.__rank(**kwargs)
            return

        # Get an ordered list of all the teams
        teams = list(
            set(
                [
                    "-".join(game[GameValues.HOME_TEAM.value].split(" "))
                    for game in total_summary
                ]
            )
        )
        num_teams = len(teams)

        # Create PageRank matrix and initial vector
        if kwargs.get("first_year"):
            vec = np.ones((num_teams, 1))
        else:
            self.year -= 1
            self.alpha -= 0.1

            kwargs["serialize_results"] = False
            kwargs["first_year"] = True
            vec = self.__rank(**kwargs)

        num_teams = max(num_teams, len(vec))
        mat = np.zeros((num_teams, num_teams))
        for game in total_summary:
            # We only want to count games where both teams are D1 (in teams list)
            # We choose to only look at games where the first team won so we don't double-count games
            if (
                game[GameValues.HOME_TEAM.value] in teams
                and game[GameValues.AWAY_TEAM.value] in teams
                and game[GameValues.WIN_LOSS.value]
            ):
                # Game winner
                # Since we know the first/home team won, we can already assign the weight for that
                home_pr_score, away_pr_score = GameWeights.WEIGHTS.value[0], 0.0

                # Effective field goal percentage
                if game[GameValues.HOME_eFGp.value] > game[GameValues.AWAY_eFGp.value]:
                    home_pr_score += GameWeights.WEIGHTS.value[1]
                elif (
                    game[GameValues.AWAY_eFGp.value] > game[GameValues.HOME_eFGp.value]
                ):
                    away_pr_score += GameWeights.WEIGHTS.value[1]

                # Turnover percentage
                if game[GameValues.HOME_TOVp.value] < game[GameValues.AWAY_TOVp.value]:
                    home_pr_score += GameWeights.WEIGHTS.value[2]
                elif (
                    game[GameValues.AWAY_TOVp.value] < game[GameValues.HOME_TOVp.value]
                ):
                    away_pr_score += GameWeights.WEIGHTS.value[2]

                # Offensive rebound percentage
                if game[GameValues.HOME_ORBp.value] > game[GameValues.AWAY_ORBp.value]:
                    home_pr_score += GameWeights.WEIGHTS.value[3]
                elif (
                    game[GameValues.AWAY_ORBp.value] > game[GameValues.HOME_ORBp.value]
                ):
                    away_pr_score += GameWeights.WEIGHTS.value[3]

                # Free throw rate
                if game[GameValues.HOME_FTR.value] > game[GameValues.AWAY_FTR.value]:
                    home_pr_score += GameWeights.WEIGHTS.value[4]
                elif game[GameValues.AWAY_FTR.value] > game[GameValues.HOME_FTR.value]:
                    away_pr_score += GameWeights.WEIGHTS.value[4]

                # Add weighted score for this game to matrix for both teams
                home_idx = teams.index(game[GameValues.HOME_TEAM.value])
                away_idx = teams.index(game[GameValues.AWAY_TEAM.value])

                mat[home_idx, away_idx] += home_pr_score
                mat[away_idx, home_idx] += away_pr_score

        # Alter the matrix to take into account our alpha factor
        mat = (self.alpha * mat) + (1 - self.alpha) * np.ones(
            (num_teams, num_teams)
        ) / num_teams

        # Perform many iterations of matrix multiplication
        for i in range(self.iters):
            vec = mat @ vec
            vec *= num_teams / sum(vec)  # Keep weights summed to set value (numerator)

        # Sort the (ranking, team) pair into a list of tuples
        sorted_pairs = sorted([(prob[0], team) for team, prob in zip(teams, vec)])

        # Print ranking pairs if specificed
        if kwargs.get("print_rankings"):
            for i in range(len(sorted_pairs)):
                print(num_teams - i, sorted_pairs[i])

        # Serialize results if specificed
        if kwargs.get("serialize_results"):
            # Make the year folder
            outfile1 = f"./predictions/{self.year}_rankings.p"
            outfile2 = f"./predictions/{self.year}_vector.p"
            os.makedirs(os.path.dirname(outfile1), exist_ok=True)

            serial = dict()
            for team in teams:
                serial.setdefault(team, 0)
            for item in sorted_pairs:
                serial[item[1]] = item[0]

            pickle.dump(serial, open(outfile1, "wb"))
            pickle.dump(vec, open(outfile2, "wb"))

        # Plot graph of rankings if specified
        if kwargs.get("plot_rankings"):
            s = sorted(vec)
            bins = np.arange(0.0, 3.5, 0.125)
            hist, bins = np.histogram(s, bins=bins)
            plt.hist(bins[:-1], bins, weights=hist)
            plt.show()

        return vec

    def __build_model(self):
        # Get info about each team as attributes
        self._rankings = pickle.load(
            open(f"./predictions/{self.year}_rankings.p", "rb")
        )
        self._vec = pickle.load(open(f"./predictions/{self.year}_vector.p", "rb"))
        self._df = chi2.fit(self._vec)[0]
        self._min_vec, self._max_vec = min(self._vec)[0], max(self._vec)[0]

    def compare_teams(self, teamA: str, teamB: str) -> float:
        """
        Compare two teams from the same year.

        Returns the probability that teamA will win.
        """

        rankA, rankB = self._rankings[teamA], self._rankings[teamB]

        diff = (
            chi2.cdf(self._max_vec, df=self._df) - chi2.cdf(self._min_vec, df=self._df)
        ) / sqrt(2)
        a, b = chi2.cdf(rankA, df=self._df), chi2.cdf(rankB, df=self._df)
        prob = min(abs(a - b) / diff + 0.5, 0.999)

        if rankA >= rankB:
            return prob
        else:
            return 1 - prob