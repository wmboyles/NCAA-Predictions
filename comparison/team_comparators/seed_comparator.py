from math import sqrt
from scipy.stats import norm

from .team_comparator import TeamComparator
from ..game_attrs import Team


class SeedComparator(TeamComparator):
    """
    Compares two teams based on their seed in whichever tournament they are both from.
    The lower seeded team will always have better odds of winning.
    """

    def __init__(self, stdev=None, year=0):
        """
        Create seed comparator with optional standard deviation.
        If no standard deviation is provided, the default of sqrt(68/3) (i.e. the standard deviation of [1,2,...,16]) is used.
        """

        super().__init__(year)

        self.stdev = stdev
        if stdev is None:
            # standard deviation of [1,2,...,16]
            self.stdev = sqrt(68 / 3)

    def compare_teams(self, teamA: Team, teamB: Team) -> float:
        """
        Compare two teams by finding normcdf(mean=seedA - seedB, stdev=stdev) from -inf to 0.
        This implicitly assumes that each team's ability in a game is normal with mean of their seed and standard deviation of stdev / sqrt(2).
        Thus, we are finding the probability that team A's ability is greater than team B's ability.
        """

        return norm.cdf(0, loc=teamA.seed - teamB.seed, scale=self.stdev)
