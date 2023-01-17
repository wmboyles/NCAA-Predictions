import pickle
import networkx as nx
from collections import defaultdict

from ..game_attrs import GameValues, TeamSeeding
from .team_comparators import TeamComparator


def resistance(G: nx.DiGraph) -> dict[tuple, float]:
    # Depth-first search to get a list of all paths from start to end
    all_paths: list[list] = []
    for start in G.nodes:
        stack, paths = [(start, [start])], []
        while stack:
            (cur, path_to_cur) = stack.pop()
            for neighbor in set(G.neighbors(cur)):
                if neighbor not in path_to_cur:
                    stack.append((neighbor, path_to_cur + [neighbor]))
            paths.append(path_to_cur)

        # First path will just be [start], which we don't want
        all_paths += paths[1:]

    # Group paths by start and end node
    paths_by_start_end: dict[tuple, list] = defaultdict(list)
    for path in all_paths:
        start, end = path[0], path[-1]
        paths_by_start_end[(start, end)].append(path)

    # For each start and end node, build a graph
    graphs: dict[tuple, nx.Graph] = dict()
    for start_end, paths in paths_by_start_end.items():
        G_pair = nx.Graph()
        for path in paths:
            G_pair.add_weighted_edges_from(
                (u, v, G[u][v]["weight"]) for (u, v) in zip(path, path[1:])
            )

        graphs[start_end] = G_pair

    # For each start_end pair graph, compute the resistance between the start and end nodes
    resistances: dict[tuple, float] = dict()
    for (start, end), G_pair in graphs.items():
        resistances[(start, end)] = nx.resistance_distance(
            G_pair, start, end, weight="weight", invert_weight=True
        )

    return resistances


class ResistanceComparator(TeamComparator):
    """
    Implements a comparison method I made up. Here is how it operates:

    1. Construct a graph with vertices of all possible teams.
    2. If A beats B n times, then add a directed edge between A and B with resistance 1/n. Do this for all games
    3. Compute the resistance for all pairs of teams.
    4. Pr(A beats B) = (1 - resistance(A -> B)) / (resistance(A -> B) + resistance(B -> A))
                     = resistance(B -> A) / (resistance(A -> B) + resistance(B -> A))
    """

    def __init__(self, year: int):
        self.__rank(year)
        self.__build_model(year)

    def __rank(self, year: int):
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
            print(teamA, teamB, game[GameValues.WIN_LOSS.value])
            if teamA in teams and teamB in teams and game[GameValues.WIN_LOSS.value]:
                if G.has_edge(teamA, teamB):
                    G[teamA][teamB]["weight"] += 1
                else:
                    G.add_edge(teamA, teamB, weight=1)

        # Compute the resistance for all pairs of teams
        resistances = resistance(G)

        TeamComparator.serialize_results(year, "resistance", resistances, None)

    def __build_model(self, year: int):
        self._mat = pickle.load(
            open(f"./predictions/{year}_resistance_rankings.p", "rb")
        )

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        R_AB = self._mat[(teamA.name, teamB.name)]
        R_BA = self._mat[(teamB.name, teamA.name)]

        return R_BA / (R_AB + R_BA)
