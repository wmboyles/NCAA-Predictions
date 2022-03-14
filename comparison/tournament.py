"""
This module contians the Touranment class, which represents some power of 2 teams in a single-elimination tournament.
It uses a team comparator to simulate rounds of the tournament to make predictions.
"""

from typing import Iterator
from dataclasses import dataclass

from .team_comparators import TeamComparator


@dataclass
class TeamSeeding:
    name: str
    seed: int
    probability: float


class Tournament:
    """
    This object represents a single-elimination tournament.
    The
    There must be a power of 2 number of teams to create the tournament.
    """

    def __init__(self, teams: list):
        """
        Build tournament by entering teams like they would appear in the bracket.

        If the type of the objects in the list is not TeamSeeding, it will be converted to one.
        Othwerwise, the list will be used as is.

        NOTE: For the NCAA tournament, the seed ordering you enter should be:
            [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
        The NCAA printable bracket ordering is:
            [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
        This is different. The NCAA ordering is dumb.
        """
        if len(teams) == 0:
            raise ValueError("Must have at least one team")

        if type(teams[0]) is TeamSeeding:
            self.tourney: list[TeamSeeding] = teams
        else:
            self.__build_tourney(teams)

    def __build_tourney(self, teams: list, quadrants: int = 4):
        num_teams = len(teams)

        # Make sure there are >= num_quadrants teams
        if quadrants <= 0:
            raise ValueError("Must have at least one quadrant")
        # Make sure quadrants is a power of 2
        if quadrants & (quadrants - 1) != 0:
            raise ValueError("Quadrants must be a power of 2")

        # Make sure there are at least as many teams as quadrants
        if num_teams < quadrants:
            raise ValueError(f"Must have at least as many teams as quadrants")
        # Check of num_teams is a power of 2
        if num_teams & (num_teams - 1) != 0:
            raise ValueError("Number of teams must be a power of 2")

        def get_seedings(size: int) -> Iterator[int]:
            """
            Helper function used to generate the seed ordering for the tournament.
            The size parameter is the number of teams in a quadrant.
            """
            if size == 1:
                yield 1
                return

            for seeding in get_seedings(size // 2):
                # NOTE: For 16 teams, the output is [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
                # This is different from the NCAA's dumb printable bracket ordering.
                yield seeding
                yield size - seeding + 1

        for i, seed in enumerate(get_seedings(num_teams // quadrants)):
            for quadrant in range(quadrants):
                teams[quadrant * (num_teams // quadrants) + i] = TeamSeeding(
                    teams[quadrant * (num_teams // quadrants) + i], seed, 1
                )

        self.tourney: list[TeamSeeding] = teams

    def __len__(self):
        return len(self.tourney)

    def __getitem__(self, index):
        return self.tourney[index]

    def __play_round(self, comparator: TeamComparator):
        """
        Helper function used to play a single round of the tournament.
        """
        new_tourney: list[TeamSeeding] = []
        for i in range(0, len(self), 2):
            teamA, teamB = self[i], self[i + 1]

            pr_A_wins = comparator.compare_teams(teamA.name, teamB.name)

            winner = teamA if pr_A_wins >= 0.5 else teamB
            loser = teamB if pr_A_wins >= 0.5 else teamA
            pr = pr_A_wins if winner is teamA else 1 - pr_A_wins

            print(f"{winner.name} beats {loser.name} ({pr:.2%})")

            if winner.seed > loser.seed:
                print(f"\t{winner.seed} {loser.seed} UPSET")

            winner.probability *= pr
            new_tourney.append(winner)

        self.tourney = new_tourney

    def simulate(self, comparator: TeamComparator):
        """
        Simulate the tournament until there is only one team left.
        """

        while len(self) > 1:
            self.__play_round(comparator)
