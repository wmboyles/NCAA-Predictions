from collections import namedtuple
from typing import Iterator


TeamSeeding = namedtuple("TeamSeeding", ["name", "seed", "probability"])


class Tournament:
    """
    This object represents a single-elimination tournament.
    The
    There must be a power of 2 number of teams to create the tournament.
    """

    def __init__(self, teams: list):
        """
        Build tournament by entering teams like they would appear in the bracket.

        NOTE: For the NCAA tournament, the seed ordering you enter should be:
            [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
        The NCAA printable bracket ordering is:
            [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
        This is different. The NCAA ordering is dumb.
        """
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
                # return
            else:
                for seeding in get_seedings(size // 2):
                    # # We need this dumb if statement to make our seeding ordering equivalent to what the NCAA uses
                    # if (size == 4 and seeding == 2) or (
                    #     size == 8 and seeding in {2, 3, 4}
                    # ):
                    #     yield size - seeding + 1
                    #     yield seeding
                    # else:

                    # NOTE: For 16 teams, the output is [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
                    # This is different from the NCAA's dumb printable bracket ordering.
                    yield seeding
                    yield size - seeding + 1

        for i, seed in enumerate(get_seedings(num_teams // quadrants)):
            for quadrant in range(quadrants):
                teams[quadrant * (num_teams // quadrants) + i] = TeamSeeding(
                    teams[quadrant * (num_teams // quadrants) + i], seed, 1
                )

        self.tourney = teams

    def __len__(self):
        return len(self.tourney)

    def __getitem__(self, index):
        return self.tourney[index]
