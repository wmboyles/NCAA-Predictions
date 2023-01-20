import pickle
from math import inf

import networkx as nx
from pqdict import minpq

from ..game_attrs import GameValues, TeamSeeding
from .team_comparators import TeamComparator


def dijkstra(graph: nx.DiGraph, start) -> dict:
    """
    Dijkstra's algorithm for finding the shortest path from start node in a weighted digraph.
    """

    # Distances contains known shortest distances from start to key nodes.
    distances = dict()
    # Assign all nodes a priority of infinity, except the start node
    pq = minpq()
    for node in graph.nodes:
        pq[node] = inf
    pq[start] = 0

    for cur, cur_dist in pq.popitems():
        distances[cur] = cur_dist

        # Look through all unvisited neighbors of the current node
        for neighbor in graph.neighbors(cur):
            if neighbor in pq:
                pq[neighbor] = min(
                    pq[neighbor], cur_dist + graph[cur][neighbor]["weight"]
                )

    return distances


class PathWeightComparator(TeamComparator):
    """
    Implements a comparison method I made up. Here is how it operates:

    1. Construct a graph with vertices of all possible teams.
    2. If A beats B n times, then add an edge between A and B with weight 1/n**2. Do this for all games
    3. Compute the shortest weighted path between all teams.
    4. Pr(A beats B)    = (1 - shortest_path_weight(A -> B)) / (shortest_path_weight(A -> B) + shortest_path_weight(B -> A))
                        = shortest_path_weight(B -> A) / (shortest_path_weight(A -> B) + shortest_path_weight(B -> A))
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

        # Invert weights of all edges
        # NOTE: The squared part is just there to make the model more confident in its predictions.
        for u, v in G.edges:
            G[u][v]["weight"] = 1 / G[u][v]["weight"] ** 2

        # Calculate all pairs shortest paths
        # We can efficiently use Dijsktra's here b/c the graph is sparse w/ |E| = O(|V|)
        min_pairs = {start: dijkstra(G, start) for start in G.nodes}

        TeamComparator.serialize_results(year, "path_weights", min_pairs, None)

    def __build_model(self, year: int):
        self._mat = pickle.load(
            open(f"./predictions/{year}_path_weights_rankings.p", "rb")
        )

    def compare_teams(self, teamA: TeamSeeding, teamB: TeamSeeding) -> float:
        sp_AB = self._mat[teamA.name][teamB.name]
        sp_BA = self._mat[teamB.name][teamA.name]

        return sp_BA / (sp_AB + sp_BA)