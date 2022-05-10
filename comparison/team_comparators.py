"""
This module contains the TeamComparator abstract base class and its concrete subclasses.
These subclasses compare two teams and give an expected probability of a team winning.
"""


import os
import pickle
from abc import ABC, abstractmethod
from math import sqrt

import data_scraping
import numpy as np
from scipy.stats import chi2, norm

from .game_attrs import GameValues, GameWeights, TeamSeeding


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

    def __init__(self, year: int, iters: int = 10000, alpha: float = 0.85):
        # Build PageRank stuff
        self.__rank(year, iters, alpha, serialize_results=True, first_year=True)
        self.__build_model(year)

    def __rank(self, year: int, iters: int, alpha: float, **kwargs: dict[str, bool]):
        """
        Uses PageRank to create a vector ranking all teams.

        KWARGS
        first_year: bool
            If False, then the previous year's rankings will be used initially.
            Otherwise, all teams start ranked equally.
        """

        total_summary = TeamComparator.get_total_summary(year)
        teams = TeamComparator.get_teams(total_summary)
        num_teams = len(teams)

        # Create PageRank matrix and initial vector
        if kwargs.get("first_year"):
            vec = np.ones((num_teams, 1))
        else:
            vec = self.__rank(year - 1, iters, alpha - 0.1, first_year=True)

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
        mat *= alpha
        mat += (1 - alpha) * np.ones((num_teams, num_teams)) / num_teams

        # Perform many iterations of matrix multiplication
        for _ in range(iters):
            vec = mat @ vec
            vec *= num_teams / sum(vec)  # Keep weights summed to set value (numerator)

        # Build rankings
        sorted_pairs = sorted([(prob[0], team) for team, prob in zip(teams, vec)])
        rankings = dict()
        for team in teams:
            rankings.setdefault(team, 0)
        for pair in sorted_pairs:
            rankings[pair[1]] = pair[0]

        TeamComparator.serialize_results(year, "pagerank", rankings, vec)

        return vec

    def __build_model(self, year: int):
        self._rankings = pickle.load(
            open(f"./predictions/{year}_pagerank_rankings.p", "rb")
        )

        vec = pickle.load(open(f"./predictions/{year}_pagerank_vector.p", "rb"))
        self._df = chi2.fit(vec)[0]
        self._min_vec, self._max_vec = min(vec)[0], max(vec)[0]

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        """
        Compare two teams from the same year.

        Returns the probability that teamA will win.
        """

        rankA, rankB = self._rankings[teamA.name], self._rankings[teamB.name]

        max_cdf = chi2.cdf(self._max_vec, df=self._df)
        min_cdf = chi2.cdf(self._min_vec, df=self._df)
        diff = (max_cdf - min_cdf) / sqrt(2)

        a_cdf, b_cdf = chi2.cdf(rankA, df=self._df), chi2.cdf(rankB, df=self._df)

        prob = min(abs(a_cdf - b_cdf) / diff + 0.5, 0.999)

        return prob if rankA >= rankB else 1 - prob


class SeedComparator(TeamComparator):
    """
    Compares two teams based on their seed in whichever tournament they are both from.
    The lower seeded team will always have better odds of winning.
    """

    def __init__(self, stdev=None):
        """
        Create seed comparator with optional standard deviation.
        If no standard deviation is provided, the default of sqrt(68/3) (i.e. the standard deviation of [1,2,...,16]) is used.
        """

        self.stdev = stdev
        if stdev is None:
            # standard deviation of [1,2,...,16]
            self.stdev = sqrt(68 / 3)

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        """
        Compare two teams by finding normcdf(mean=seedA - seedB, stdev=stdev) from -inf to 0.
        This implicitly assumes that each team's ability in a game is normal with mean of their seed and standard deviation of stdev / sqrt(2).
        Thus, we are finding the probability that team A's ability is greater than team B's ability.
        """

        return norm.cdf(0, loc=teamA.seed - teamB.seed, scale=self.stdev)


class BradleyTerryComparator(TeamComparator):
    """
    Implements Bradley-Terry model for team comparisons.
    See https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model
    """

    def __init__(self, year: int, iters: int = 1):
        self.__rank(year, iters)
        self.__build_model(year)

    def __rank(self, year: int, iters: int, **kwargs: dict[str, bool]):
        """
        Uses Bradley-Terry model to create a vector ranking all teams.

        KWARGS
        first_year: bool
            If False, then the previous year's rankings will be used initially.
            Otherwise, all teams start ranked equally.
        """

        total_summary = TeamComparator.get_total_summary(year)
        teams = TeamComparator.get_teams(total_summary)
        num_teams = len(teams)

        # Create game winning matrix and initial vector
        mat = np.zeros((num_teams, num_teams))
        for game in total_summary:
            # We only want to count games where both teams are D1 (in teams list)
            # We choose to only look at games where the first team won so we don't double-count games
            if (
                game[GameValues.HOME_TEAM.value] in teams
                and game[GameValues.AWAY_TEAM.value] in teams
                and game[GameValues.WIN_LOSS.value]
            ):
                home_idx = teams.index(game[GameValues.HOME_TEAM.value])
                away_idx = teams.index(game[GameValues.AWAY_TEAM.value])

                mat[home_idx, away_idx] += 1

        vec = np.ones((num_teams, 1)) / num_teams
        if not kwargs.get("first_year"):
            self.__rank(year - 1, iters, first_year=True)

            prev_year_rankings: dict = pickle.load(
                open(f"./predictions/{year-1}_bradleyterry_rankings.p", "rb")
            )

            for team, value in prev_year_rankings.items():
                vec[teams.index(team)] = value
        vec /= sum(vec)

        # Perform iterations of Bradley-Terry process
        for _ in range(iters):
            new_vec = np.copy(vec)
            # For each entry, p_i = (number of wins for team i) / sum((total games vs team j) / (pr_i + pr_j))
            for i in range(num_teams):
                numerator = sum(mat[i])
                denominator = sum(
                    (mat[i, j] + mat[j, i]) / (vec[i] + vec[j])
                    for j in range(num_teams)
                    if j != i
                )
                new_vec[i] = numerator / denominator

            # Make sure no vector entries are 0.
            # If they are, set them to 1 / num_teams**2
            new_vec[new_vec == 0] = 1 / num_teams**2

            # Normalize vector
            new_vec /= sum(new_vec)

            # Update vector
            vec = new_vec

        # Build rankings
        sorted_pairs = sorted([prob[0], team] for team, prob in zip(teams, vec))
        rankings = dict()
        for team in teams:
            rankings.setdefault(team, 0)
        for item in sorted_pairs:
            rankings[item[1]] = item[0]

        TeamComparator.serialize_results(year, "bradleyterry", rankings, vec)

    def __build_model(self, year: int):
        self._rankings = pickle.load(
            open(f"./predictions/{year}_bradleyterry_rankings.p", "rb")
        )

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        """
        Compare two teams from the same year.

        Returns the probability that teamA will win.
        """

        scoreA = self._rankings[teamA.name]
        scoreB = self._rankings[teamB.name]

        return scoreA / (scoreA + scoreB)


class EloComparator(TeamComparator):
    """
    Implements Elo model for team comparisons.
    See https://en.wikipedia.org/wiki/Elo_rating_system
    """

    def __init__(self, year: int):
        self.__rank(year, serialize_results=True)
        self.__build_model(year)

    def __rank(self, year: int, **kwargs: dict[str, bool | int]):
        """
        Uses Elo model to create a vector ranking all teams.

        KWARGS
        first_year: bool
            If False, then the previous year's rankings will be used initially.
            Otherwise, all teams start ranked equally.
        inital_rating: int
            Initial rating for all teams.
            The default is 1750.
        """

        total_summary = TeamComparator.get_total_summary(year)
        teams = TeamComparator.get_teams(total_summary)
        num_teams = len(teams)

        # Initialize Elo ratings of all teams
        ratings = kwargs.get("initial_rating", 1750) * np.ones((num_teams, 1))

        # Decide whether to look back or not
        if not kwargs.get("first_year"):
            self.__rank(year - 1, first_year=True)

            prev_year_ratings: dict = pickle.load(
                open(f"./predictions/{year-1}_elo_rankings.p", "rb")
            )

            for team, value in prev_year_ratings.items():
                ratings[teams.index(team)] = value

        for game in total_summary:
            # We only want to count games where both teams are D1 (in teams list)
            # We choose to only look at games where the first team won so we don't double-count games
            if (
                game[GameValues.HOME_TEAM.value] in teams
                and game[GameValues.AWAY_TEAM.value] in teams
                and game[GameValues.WIN_LOSS.value]
            ):
                home_idx = teams.index(game[GameValues.HOME_TEAM.value])
                away_idx = teams.index(game[GameValues.AWAY_TEAM.value])

                qA = 10 ** (ratings[home_idx] / 400)
                qB = 10 ** (ratings[away_idx] / 400)
                eA, eB = qA / (qA + qB), qB / (qA + qB)

                # Update Elo ratings
                min_rating = min(ratings[home_idx], ratings[away_idx])
                if min_rating < 1500:
                    K = 32
                elif 1700 <= min_rating <= 2000:
                    K = 24
                else:
                    K = 16

                ratings[home_idx] += K * (1 - eA)
                ratings[away_idx] += K * (0 - eB)

        # Build rankings
        sorted_pairs = sorted([prob[0], team] for team, prob in zip(teams, ratings))
        rankings = dict()
        for team in teams:
            rankings.setdefault(team, 0)
        for item in sorted_pairs:
            rankings[item[1]] = item[0]

        TeamComparator.serialize_results(year, "elo", rankings, ratings)

    def __build_model(self, year: int):
        self._rankings = pickle.load(open(f"./predictions/{year}_elo_rankings.p", "rb"))
        self._vec = pickle.load(open(f"./predictions/{year}_elo_vector.p", "rb"))

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        qA = 10 ** (self._rankings[teamA.name] / 400)
        qB = 10 ** (self._rankings[teamB.name] / 400)

        eA = qA / (qA + qB)

        return eA


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
