import pickle
import networkx as nx
from collections import defaultdict
from functools import reduce
from operator import add

from ..game_attrs import GameValues, Team
from .team_comparator import TeamComparator
import os

MAX_PATHS = 25_000


def resistance(
    G: nx.DiGraph, max_paths=MAX_PATHS, max_depth=10
) -> dict[tuple[Team, Team], float]:
    """
    Compute the resistance between all pairs of nodes in a weighted digraph.
    """

    # Depth-first search to get a list of all paths from start to end
    # NOTE: This method is extremely slow on even moderately sized graphs
    def find_all_paths(start: Team) -> list[list[Team]]:
        stack = [(start, [start])]
        paths: list[list[Team]] = []
        while stack and len(paths) < max_paths:
            (cur, path_to_cur) = stack.pop()
            for neighbor in set(G.neighbors(cur)):
                if neighbor not in path_to_cur and len(path_to_cur) < max_depth:
                    stack.append((neighbor, path_to_cur + [neighbor]))

            paths.append(path_to_cur)

        # paths[0] is the path from start to start, which we don't want
        return paths[1:]

    all_paths: list[list[Team]] = reduce(
        add, (find_all_paths(start) for start in G.nodes)
    )

    # Group paths by start and end node
    paths_by_start_end: dict[tuple[Team, Team]] = defaultdict(list[Team])
    for path in all_paths:
        paths_by_start_end[(path[0], path[-1])].append(path)

    # For each start and end node, build a graph
    # For each start_end pair graph, compute the resistance between the start and end nodes
    resistances: dict[tuple[Team, Team], float] = dict()
    for (start, end), paths in paths_by_start_end.items():
        G_pair = nx.Graph()
        G_pair.add_weighted_edges_from(
            (u, v, G[u][v]["weight"])
            for path in paths
            for (u, v) in zip(path, path[1:])
        )
        resistances[(start, end)] = nx.resistance_distance(G_pair, start, end, weight="weight", invert_weight=True)

    return resistances


class ResistanceComparator(TeamComparator):
    """
    Implements a comparison method I made up. Here is how it operates:

    1. Construct a graph with vertices of all possible teams.
    2. If A beats B n times, then add a directed edge between A and B with resistance 1/n. Do this for all games
    3. Compute the resistance for all pairs of teams.
    4. Pr(A beats B) = (1 - resistance(A -> B)) / (resistance(A -> B) + resistance(B -> A))
                     = resistance(B -> A) / (resistance(A -> B) + resistance(B -> A))

    NOTE: This method is extremely slow on even moderately sized graphs.
    You must limit max_paths and max_depth to complete in a reasonable amount of time.
    """

    def __init__(self, year: int, max_paths: int = MAX_PATHS):
        super().__init__(year)

        if not os.path.exists(f"./predictions/{year}_resistance_rankings.p"):
            self.__rank(year, max_paths)

        self.__build_model(year)

    def __rank(self, year: int, max_paths: int):
        total_summary = TeamComparator.get_total_summary(year)
        teams = TeamComparator.get_teams(total_summary)

        # Construct a graph with vertices of all possible teams
        G = nx.DiGraph()
        for game in total_summary:
            # We only want to count games where both teams are D1 (in teams list)
            # We choose to only look at games where the first team won so we don't double-count games
            # NOTE: These HOME_TEAM and AWAY_TEAM do not literally tell us if a team is home or away
            teamA = game[GameValues.HOME_TEAM.value]
            teamB = game[GameValues.AWAY_TEAM.value]
            # print(teamA, teamB, game[GameValues.WIN_LOSS.value])
            if teamA in teams and teamB in teams and game[GameValues.WIN_LOSS.value]:
                if G.has_edge(teamA, teamB):
                    G[teamA][teamB]["weight"] += 1
                else:
                    G.add_edge(teamA, teamB, weight=1)

        # Compute the resistance for all pairs of teams
        # NOTE: No need to invert weight, as nx.resistance_distance does this for us
        resistances = defaultdict(dict)
        for (start, end), ohms in resistance(G, max_paths).items():
            resistances[start][end] = ohms

        TeamComparator.serialize_results(year, "resistance", resistances, None)

    def __build_model(self, year: int):
        self._mat = pickle.load(
            open(f"./predictions/{year}_resistance_rankings.p", "rb")
        )

    def compare_teams(self, a: Team, b: Team) -> float:
        if a == b:
            return 0.5

        a_to_b = b.name in self._mat[a.name]
        b_to_a = a.name in self._mat[b.name]
        match (a_to_b, b_to_a):
            case (False, False):
                print(
                    f"WARNING: {a.name} and {b.name} are not comparable via resistance. Defaulting to seed comparison."
                )
                return b.seed / (a.seed + b.seed)
            case (False, _):
                print(
                    f"INFO: No paths sampled for {a.name} -> {b.name}. Assuming {b.name} wins 99%"
                )
                return 0.01
            case (_, False):
                print(
                    f"INFO: No paths sampled for {b.name} -> {a.name}. Assuming {a.name} wins 99%"
                )
                return 0.99

        R_AB = self._mat[a.name][b.name]
        R_BA = self._mat[b.name][a.name]

        return R_BA / (R_AB + R_BA)
