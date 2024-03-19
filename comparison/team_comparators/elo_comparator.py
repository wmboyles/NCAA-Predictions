import pickle
import numpy as np

from .team_comparator import TeamComparator
from ..game_attrs import GameValues, Team


class EloComparator(TeamComparator):
    """
    Implements Elo model for team comparisons.
    See https://en.wikipedia.org/wiki/Elo_rating_system
    """

    def __init__(self, year: int, gender: str):
        super().__init__(year, gender)
        self.__rank(year, gender)
        self.__build_model(year, gender)

    def __rank(self, year: int, gender: str, **kwargs: dict[str, bool | int]):
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

        total_summary = TeamComparator.get_total_summary(year, gender)
        teams = TeamComparator.get_teams(total_summary)
        num_teams = len(teams)

        # Initialize Elo ratings of all teams
        ratings = kwargs.get("initial_rating", 1750) * np.ones((num_teams, 1))

        # Decide whether to look back or not
        if not kwargs.get("first_year"):
            self.__rank(year - 1, gender, first_year=True)

            prev_year_ratings: dict = pickle.load(
                open(f"./predictions/{gender}/{year-1}_elo_rankings.p", "rb")
            )

            for team, value in prev_year_ratings.items():
                try:
                    ratings[teams.index(team)] = value
                except ValueError:  # Team was not in the previous year's data (new to Division I)
                    pass

        for game in total_summary:
            # We only want to count games where both teams are D1 (in teams list)
            # We choose to only look at games where the first team won so we don't double-count games
            # NOTE: These HOME_TEAM and AWAY_TEAM do not literally tell us if a team is home or away
            teamA = game[GameValues.HOME_TEAM.value]
            teamB = game[GameValues.AWAY_TEAM.value]
            if teamA in teams and teamB in teams and game[GameValues.WIN_LOSS.value]:
                home_idx = teams.index(teamA)
                away_idx = teams.index(teamB)

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

        TeamComparator.serialize_results(year, "elo", rankings, ratings, gender)

    def __build_model(self, year: int, gender: str):
        self._rankings = pickle.load(open(f"./predictions/{gender}/{year}_elo_rankings.p", "rb"))
        self._vec = pickle.load(open(f"./predictions/{gender}/{year}_elo_vector.p", "rb"))

    def compare_teams(self, a: Team, b: Team) -> float:
        qA = 10 ** (self._rankings[a.name] / 400)
        qB = 10 ** (self._rankings[b.name] / 400)

        eA = qA / (qA + qB)

        return eA
