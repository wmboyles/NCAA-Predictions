from typing import Iterator

from .team_comparators.team_comparator import TeamComparator
from .game_attrs import Team

from dataclasses import dataclass
from collections import defaultdict


@dataclass
class GameResult:
    """
    A GameResult is a a mapping of teams for probabilities.
    The sum of the probabilities over all teams should be 1.
    These probabilities represent a superposition of all possible outcomes of a game
    according to some TeamComparator.
    """

    probabilities: defaultdict[Team, float]

    @classmethod
    def single_team(cls, team: Team) -> "GameResult":
        """
        Creates a GameResult with a single team with probability 1.
        This is useful for representing a team's initial seeding in a tournament.
        """

        return cls(defaultdict(float, {team: 1.0}))


TeamNestedTuple = (
    tuple[Team, Team],
    tuple[Team, "TeamNestedTuple"] | tuple[Team, "TeamNestedTuple"] | Team,
)


@dataclass
class Tournament:
    """
    A Tournament is a binary tree of GameResults.
    This allows us to cleanly represent any single-elimination tournament structure,
    including conference tournaments where teams have byes.

    TODO: Extend `round_winners` to get the probability of each team winning that round, regardless of the probability of making it to that round.
    """

    matchup: tuple["Tournament", "Tournament"] | GameResult

    @classmethod
    def _single_team(cls, team: Team) -> "Tournament":
        return cls(GameResult.single_team(team))

    @classmethod
    def from_nested_tuple(cls, t: TeamNestedTuple) -> "Tournament":
        """
        Creates a Tournament from a nested tuple of teams.
        Visually,

            ```text
                                          +--B
                                          |
            (A, (B, (C, D)))  <==>  A--*--|
                                          |  +--C
                                          +--|
                                             +--D
            ```

        Note that (((A, A), (A, A)), ((B, B), (C, D))) will give a mathematically identical tournament as above.
        """

        if isinstance(t, Team):
            return cls._single_team(t)

        left, right = t
        left_tournament, right_tournament = cls.from_nested_tuple(
            left
        ), cls.from_nested_tuple(right)
        return cls((left_tournament, right_tournament))

    @classmethod
    def from_team_list(cls, teams: list[Team]) -> "Tournament":
        """
        Creates a Tournament from a list of teams by pairing neighboring teams together.
        For example, if the list is [A, B, C, D], then the resulting Tournament will be ((A, B), (C, D)).
        Or visually,

            ```text
            A--+     +--C
               |--*--|
            B--+     +--D
            ```

        If you want to create a tournament structure with byes, you can list the same team multiple times consecutively.
        For example, if the list is [A, A, B, C], then the resulting Tournament will be ((A, A), (B, C)).
        Or visually,

            ```text
            A--+     +--B              +--B
               |--*--|     <==>  A--*--|
            A--+     +--C              +--C
            ```

        Use this method when you want to explicitly give teams a seed and `from_name_list` otherwise.
        """

        if len(teams) == 1:
            return cls._single_team(teams[0])

        left, right = teams[: len(teams) // 2], teams[len(teams) // 2 :]

        left_tournament, right_tournament = cls.from_team_list(
            left
        ), cls.from_team_list(right)
        return cls((left_tournament, right_tournament))

    @classmethod
    def from_name_list(cls, names: list[str], quadrants=4) -> "Tournament":
        """
        Creates a Tournament from a list of team names, a default seeding.
        This method requires that the number of teams be a power of 2 because it creates a full and balanced binary tree structure.
        However, you can use the tricks described in `from_team_list` to represent different structures.

        The default seeds are the numbers 1..n, where n is the number of teams in a quadrant.
        By default, there are 4 `quadrants` like you would see in the NCAA tournament.

        NOTE: For 64 teams like in the NCAA tournament, the seed ordering is
        [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
        This is different from the NCAA's dumb printable bracket ordering.
        We choose this ordering because it is extendible to quadrants of different sizes,
        while the NCAA's ordering makes no recursive sense.
        """

        num_teams = len(names)

        if num_teams < quadrants:
            raise ValueError(f"Must have at least as many teams as quadrants")
        if num_teams & (num_teams - 1) != 0:
            raise ValueError("Number of teams must be a power of 2")

        def get_seedings(size: int) -> Iterator[int]:
            """
            Helper function used to generate the seed ordering for the tournament.
            `size` is the number of teams in a quadrant.
            """

            if size == 1:
                yield 1
                return

            for seeding in get_seedings(size // 2):
                yield seeding
                yield size - seeding + 1

        teams: list[Team] = [None] * num_teams
        for i, seed in enumerate(get_seedings(num_teams // quadrants)):
            for quadrant in range(quadrants):
                teams[quadrant * (num_teams // quadrants) + i] = Team(
                    names[quadrant * (num_teams // quadrants) + i], seed
                )

        return cls.from_team_list(teams)

    def __len__(self):
        if isinstance(self.matchup, GameResult):
            return 1
        return sum(len(x) for x in self.matchup)

    @classmethod
    def _round(
        cls, a: GameResult, b: GameResult, comparator: TeamComparator
    ) -> GameResult:
        result: defaultdict[Team, float] = defaultdict(float)

        for (ta, pa) in a.probabilities.items():
            result[ta] += pa * sum(
                pb * comparator.compare_teams(ta, tb)
                for (tb, pb) in b.probabilities.items()
            )
        for (tb, pb) in b.probabilities.items():
            result[tb] += pb * sum(
                pa * comparator.compare_teams(tb, ta)
                for (ta, pa) in a.probabilities.items()
            )

        return GameResult(result)

    def _leaves(self) -> list[GameResult]:
        """
        Get all the tree nodes of type GameResult.
        These represent completed games at some point in the tournament.
        """

        if isinstance(self.matchup, GameResult):
            return [self.matchup]

        left, right = self.matchup
        return left._leaves() + right._leaves()

    def play_round(self, comparator) -> "Tournament":
        """
        Creates a new Tournament by playing the next round of games.
        This converts nodes that are parents to leaf nodes into leaf nodes.
        For example, if we had the tournament ((A, B), (C, D)),
        then this method would return (GameResult(A, B), GameResult(C, D)),
        where GameResult(A, B) is the result of the game between A and B, according to the `comparator`.
        Or visually,

            ```text
            A--+     +--C
               |--*--|     <==>  GameResult(A, B)--*--GameResult(C, D)
            B--+     +--D
            ```

        If you keep calling this method on the this method's results,
        then you will eventually get a Tourament with a single GameResult root node.
        The probabilities in that node are the probabilities of each team winning the entire tournament,
        according to your choice of `comparator`.
        """

        if isinstance(self.matchup, GameResult):
            return self

        left, right = self.matchup
        if isinstance(left.matchup, GameResult) and isinstance(
            right.matchup, GameResult
        ):
            left_winner = max(left.matchup.probabilities, key=left.matchup.probabilities.get)
            right_winner = max(right.matchup.probabilities, key=right.matchup.probabilities.get)

            matchup_result = self._round(left.matchup, right.matchup, comparator)
            matchup_winner = max(matchup_result.probabilities, key=matchup_result.probabilities.get)
            matchup_loser = left_winner if matchup_winner == right_winner else right_winner

            is_upset = matchup_winner.seed > matchup_loser.seed

            print(f"{matchup_winner.name} beats {matchup_loser.name}{" (upset)" if is_upset else ""}")

            return Tournament(matchup_result)

        return Tournament((left.play_round(comparator), right.play_round(comparator)))

    def round_winners(self) -> list[Team]:
        """
        Return the most probable Team in each leaf node.
        """

        return [
            max(leaf.probabilities, key=leaf.probabilities.get)
            for leaf in self._leaves()
        ]

    def _depth(self) -> int:
        """
        Max number of levels in the tree.
        That is, the max number of games a team would need to play to win the tournament.
        """

        if isinstance(self.matchup, GameResult):
            return 0

        left, right = self.matchup
        return 1 + max(left._depth(), right._depth())

    def normalize(self) -> "Tournament":
        """
        Converts a tournament into a tournament with different structure into
        an equivalent tournament with a power of 2 number of teams.
        It does this by duplicating teams with byes.
        """

        max_depth = self._depth()

        def normalize_helper(t: Tournament, depth: int) -> Tournament:
            if not isinstance(t.matchup, GameResult):
                left, right = t.matchup
                left_normalized = normalize_helper(left, depth + 1)
                right_normalized = normalize_helper(right, depth + 1)

                return Tournament((left_normalized, right_normalized))

            if depth == max_depth:
                return t

            # TODO: Could improve by making 2**(max_depth - depth) copies?
            left_normalized = normalize_helper(t, depth + 1)
            right_normalized = normalize_helper(t, depth + 1)

            return Tournament((left_normalized, right_normalized))

        return normalize_helper(self, 0)
