import pickle

import numpy as np

from .team_comparators import TeamComparator

from ..game_attrs import GameValues, TeamSeeding


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
