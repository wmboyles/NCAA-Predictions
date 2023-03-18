import pickle
from math import sqrt
import numpy as np
from scipy.stats import chi2
import os

from .team_comparator import TeamComparator
from ..game_attrs import GameValues, GameWeights, Team


class PageRankComparator(TeamComparator):
    """
    Ranks all Division I NCAA Basketball teams in a given year using PageRank.
    See https://en.wikipedia.org/wiki/PageRank
    """

    def __init__(
        self, year: int, gender: str, iters: int = 10_000, alpha: float = 0.85
    ):
        """
        Args:
            year:
                The year that the NCAA championship game takes place.
                The 2019-2020 season would correpond to year=2020.
            alpha:
                A value between 0 and 1 that is a measure of randomness in
                PageRank meant to model the possibility that a user randomly
                navigates to a page without using a link. alpha=1 would be
                completely deterministic, while alpha=0 would be completely
                random. Google is rumored to use alpha=.85.
            iters:
                The number of iterations of PageRank matrix multiplication to
                perform. The default of iters=10_000, about 30x the number of
                Division I teams, is generally sufficient for ranking.
        """
        super().__init__(year, gender)

        if not os.path.exists(f"./predictions/{gender}/{year}_pagerank_rankings.p"):
            self.__rank(
                year, gender, iters, alpha, serialize_results=True, first_year=True
            )

        self.__build_model(year, gender)

    def __rank(
        self,
        year: int,
        gender: str,
        iters: int,
        alpha: float,
        **kwargs: dict[str, bool],
    ):
        """
        Uses PageRank to create a vector ranking all teams.

        Kwargs:
            first_year: bool
                If False, then the previous year's rankings will be used initially.
                Otherwise, all teams start ranked equally.
        """

        total_summary = TeamComparator.get_total_summary(year, gender)
        teams = TeamComparator.get_teams(total_summary)
        num_teams = len(teams)

        # Create PageRank matrix and initial vector
        if kwargs.get("first_year"):
            vec = np.ones((num_teams, 1))
        else:
            vec = self.__rank(year - 1, gender, iters, alpha - 0.1, first_year=True)

        num_teams = max(num_teams, len(vec))
        mat = np.zeros((num_teams, num_teams))
        for game in total_summary:
            # We only want to count games where both teams are D1 (in teams list)
            # We choose to only look at games where the first team won so we don't double-count games
            # NOTE: These HOME_TEAM and AWAY_TEAM do not literally tell us if a team is home or away
            teamA = game[GameValues.HOME_TEAM.value]
            teamB = game[GameValues.AWAY_TEAM.value]
            if teamA in teams and teamB in teams and game[GameValues.WIN_LOSS.value]:
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
                home_idx = teams.index(teamA)
                away_idx = teams.index(teamB)

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

        TeamComparator.serialize_results(year, "pagerank", rankings, vec, gender)

        return vec

    def __build_model(self, year: int, gender: str):
        self._rankings = pickle.load(
            open(f"./predictions/{gender}/{year}_pagerank_rankings.p", "rb")
        )

        vec = pickle.load(open(f"./predictions/{gender}/{year}_pagerank_vector.p", "rb"))
        self._df = chi2.fit(vec)[0]
        self._min_vec, self._max_vec = min(vec)[0], max(vec)[0]

    def compare_teams(self, a: Team, b: Team) -> float:
        """
        Compare two teams from the same year.

        Returns the probability that a will win.
        """

        rankA, rankB = self._rankings[a.name], self._rankings[b.name]

        max_cdf = chi2.cdf(self._max_vec, df=self._df)
        min_cdf = chi2.cdf(self._min_vec, df=self._df)
        diff = (max_cdf - min_cdf) / sqrt(2)

        a_cdf, b_cdf = chi2.cdf(rankA, df=self._df), chi2.cdf(rankB, df=self._df)

        prob = min(abs(a_cdf - b_cdf) / diff + 0.5, 0.999)

        return prob if rankA >= rankB else 1 - prob
