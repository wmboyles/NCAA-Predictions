import numpy as np
import pickle
import os
from math import sqrt
from scipy.stats import chi2

import harvester

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from enum import Enum


class GameValues(Enum):
    """
    Items in this enum are the different indexes of the "four factor" statistics
    that the cleaner program extracts and claculates for each game.
    To use their value, you'd write game[GameValue.ITEM.value]

    In all instances, a high value of game[GameValue.ITEM.value] means a better team
    """

    HOME_TEAM = 0  # Name of first (called home but not always) team
    AWAY_TEAM = 1  # Name of second (called away but not always) team

    WIN_LOSS = 2  # Did the home/first team win?

    HOME_SCORE = 3  # The home/first team's score
    AWAY_SCORE = 4  # The away/second team's score

    HOME_eFGp = 5  # The home/first team's effective field goal percentage
    AWAY_eFGp = 6  # The away/second team's effective field goal percentage

    HOME_TOVp = 7  # The home/first team's turnover percentage
    AWAY_TOVp = 8  # The away/second team's turnover percentage

    HOME_ORBp = 9  # The home/first team's offensive rebound percentage
    AWAY_ORBp = 10  # The away/second team's offensive rebound percentage

    HOME_FTR = 11  # The home/first team's free throw rate
    AWAY_FTR = 12  # The away/second team's free throw rate


class GameWeights(Enum):
    """
    Items in this enum are the weights of a team winning game and the
    "four factors":
        Effective field goal percentage
        Turnover percentage
        Offensive rebound percentage
        Free throw rate.
    These weights can be changed to change the importance of these factors in each game.
    """

    WEIGHTS = [50, 13.3333, 6.6666, 8.3333, 5]


def rank(
    year,
    alpha=0.85,
    iters=3500,
    print_rankings=False,
    plot_rankings=False,
    serialize_results=True,
    first_year=True,
):
    """
    Ranks all Division I NCAA Basketball teams in a given year using PageRank.
    PARAMETERS
    year -->    The year that the NCAA championship game takes place.
                The 2019-2020 season would correpond to year=2020.
    alpha -->   A value between 0 and 1 that is a measure of randomness in
                PageRank meant to model the possibility that a user randomly
                navigates to a page without using a link. alpha=1 would be
                completely deterministic, while alpha=0 would be completely
                random. Google is rumored to use alpha=.85.
    iters -->   The number of iterations of PageRank matrix multiplication to
                perform. The default of iters=3500, about 10x the number of
                Division I teams, is generally sufficient for ranking.
    print_rankings -->  Should the function print out its rankings to stdout?
                        Defaults to False.
    plot_rankings -->   Should the function plot the rankings in sorted order?
                        Defaults to False.
    serialize_results -->   Should the function save its rankings to a .p file
                            called "./predictions/[YEAR]/rankings.p"?
                            Defaults to True.
    """

    # Try to deserialize .p file summary. Try to create it if it doesn't exist
    try:
        total_summary = pickle.load(
            open("./summaries/" + str(year) + "/total_summary.p", "rb")
        )
    except FileNotFoundError:
        print("--- WARNING: No summary found for", year, "Trying to create summary...")
        try:
            harvester.harvest(year)
        except:
            print("--- ERROR: Could not make summary for", year)
            return
        print("--- SUCCESS: Summary created for", year)
        print("--- Trying to rank again with newly created summary")
        rank(year, alpha, iters, print_rankings, plot_rankings, serialize_results)
        return

    # Get an ordered list of all the teams
    teams = list(
        set(
            [
                "-".join(game[GameValues.HOME_TEAM.value].split(" "))
                for game in total_summary
            ]
        )
    )
    num_teams = len(teams)

    # Create PageRank matrix and initial vector
    if first_year:
        vec = np.ones((num_teams, 1))
    else:
        vec = rank(year - 1, alpha - 0.1, serialize_results=False, first_year=True)

    num_teams = max(num_teams, len(vec))
    mat = np.zeros((num_teams, num_teams))
    for game in total_summary:
        # We only want to count games where both teams are D1 (in teams list)
        # We choose to only look at games where the first team won so we don't double-count games
        if (
            game[GameValues.HOME_TEAM.value] in teams
            and game[GameValues.AWAY_TEAM.value] in teams
            and game[GameValues.WIN_LOSS.value]
        ):
            # Game winner
            # Since we know the first/home team won, we can already assign the weight for that
            home_pr_score, away_pr_score = GameWeights.WEIGHTS.value[0], 0.0

            # Effective field goal percentage
            if game[GameValues.HOME_eFGp.value] > game[GameValues.AWAY_eFGp.value]:
                home_pr_score += GameWeights.WEIGHTS.value[1]
            elif game[GameValues.AWAY_eFGp.value] > game[GameValues.HOME_eFGp.value]:
                away_pr_score += GameWeights.WEIGHTS.value[1]

            # Turnover percentage
            if game[GameValues.HOME_TOVp.value] < game[GameValues.AWAY_TOVp.value]:
                home_pr_score += GameWeights.WEIGHTS.value[2]
            elif game[GameValues.AWAY_TOVp.value] < game[GameValues.HOME_TOVp.value]:
                away_pr_score += GameWeights.WEIGHTS.value[2]

            # Offensive rebound percentage
            if game[GameValues.HOME_ORBp.value] > game[GameValues.AWAY_ORBp.value]:
                home_pr_score += GameWeights.WEIGHTS.value[3]
            elif game[GameValues.AWAY_ORBp.value] > game[GameValues.HOME_ORBp.value]:
                away_pr_score += GameWeights.WEIGHTS.value[3]

            # Free throw rate
            if game[GameValues.HOME_FTR.value] > game[GameValues.AWAY_FTR.value]:
                home_pr_score += GameWeights.WEIGHTS.value[4]
            elif game[GameValues.AWAY_FTR.value] > game[GameValues.HOME_FTR.value]:
                away_pr_score += GameWeights.WEIGHTS.value[4]

            # Add weighted score for this game to matrix for both teams
            home_idx = teams.index(game[GameValues.HOME_TEAM.value])
            away_idx = teams.index(game[GameValues.AWAY_TEAM.value])

            mat[home_idx, away_idx] += home_pr_score
            mat[away_idx, home_idx] += away_pr_score

    # Alter the matrix to take into account our alpha factor
    mat = (alpha * mat) + (1 - alpha) * np.ones((num_teams, num_teams)) / num_teams

    # Perform many iterations of matrix multiplication
    for i in range(iters):
        vec = mat @ vec
        vec *= num_teams / sum(vec)  # Keep weights summed to set value (numerator)

    # Sort the (ranking, team) pair into a list of tuples
    sorted_pairs = sorted([(prob[0], team) for team, prob in zip(teams, vec)])

    # Print ranking pairs if specificed
    if print_rankings:
        for i in range(len(sorted_pairs)):
            print(num_teams - i, sorted_pairs[i])

    # Serialize results if specificed
    # TODO: Serialize results as dict?
    if serialize_results:
        # Make the year folder
        outfile1 = f"./predictions/{year}_rankings.p"
        outfile2 = f"./predictions/{year}_vector.p"
        os.makedirs(os.path.dirname(outfile1), exist_ok=True)

        serial = dict()
        for team in teams:
            serial.setdefault(team, 0)
        for item in sorted_pairs:
            serial[item[1]] = item[0]

        pickle.dump(serial, open(outfile1, "wb"))
        pickle.dump(vec, open(outfile2, "wb"))

    # Plot graph of rankings if specified
    if plot_rankings:
        s = sorted(vec)
        bins = np.arange(0.0, 3.5, 0.125)
        hist, bins = np.histogram(s, bins=bins)
        plt.hist(bins[:-1], bins, weights=hist)
        plt.show()

    return vec


def compare_teams(
    teamA: str,
    teamB: str,
    rankA: float,
    rankB: float,
    seedA: int,
    seedB: int,
    df: float,
    min_vec: float,
    max_vec: float,
    print_out: bool = False,
):
    """
    Compare two teams from the same year.

    teamA: str
        Name of first team to compare
    teamB: str
        Name of second team to compare
    rankA: float
        PageRank score of first team to compare
    rankB: float
        PageRank score of second team to compare
    df: float
        Degrees of freedom determined by chi squared model of all teams from year
    min_vec: float
        The minimum PageRank score of all teams from year
    max_vec: float
        The maximum PageRank score of all teams from year
    print_out: bool
        Prints "[Winning Team] beats [Losing Team]: [Confidence Level]" if true.
        Defaults to false.
    """

    diff = (chi2.cdf(max_vec, df=df) - chi2.cdf(min_vec, df=df)) / sqrt(2)
    a, b = chi2.cdf(rankA, df=df), chi2.cdf(rankB, df=df)
    prob = min(abs(a - b) / diff + 0.5, 0.999)

    if rankA >= rankB:
        if print_out:
            print(f"{teamA} ({seedA}) beats {teamB} ({seedB}): {prob}")
        return prob
    else:
        if print_out:
            print(f"{teamB} ({seedB}) beats {teamA} ({seedA}): {prob}")
        return 1 - prob


def build_tourney(rankings: list) -> list:
    """
    Given a list of teams in ranked order, reorder them in NCAA bracket format.
    NCAA Bracket Format:
    1) In any list of teams of length the #1 ranked team should play the #L ranked team in the first round
    2) In any list of teams, the 1st and 2nd best teams shouldn't play each other until the final round.
    """
    if len(rankings) <= 1:
        return rankings

    left_rankings, right_rankings = [], []

    # pointer to current tourney we're building
    cur = left_rankings

    # We start by adding the top team to the first half, then add the second and third teams to the second half
    side_adds = 1
    for seed in rankings:
        cur.append(seed)

        side_adds += 1

        if side_adds >= 2:
            if cur is left_rankings:
                cur = right_rankings
            else:
                cur = left_rankings
            side_adds = 0

    tourney = build_tourney(left_rankings) + build_tourney(right_rankings)
    return tourney


def simulate_tourney(year: int, tourney: list) -> list:
    rankings = pickle.load(open("./predictions/" + str(year) + "_rankings.p", "rb"))
    vec = pickle.load(open("./predictions/" + str(year) + "_vector.p", "rb"))

    df = chi2.fit(vec)[0]
    min_vec, max_vec = min(vec)[0], max(vec)[0]

    rounds = [tourney]
    while len(tourney) > 1:
        print(tourney)
        print("--------------------------------------------------")

        new_tourney = []
        for i in range(0, len(tourney), 2):
            # team name, seed in bracket, model's probability that they advance to current position
            teamA, seedA, prA = tourney[i]
            rankA = rankings[teamA]

            teamB, seedB, prB = tourney[i + 1]
            rankB = rankings[teamB]

            A_beats_B = compare_teams(
                teamA,
                teamB,
                rankA,
                rankB,
                seedA,
                seedB,
                df,
                min_vec,
                max_vec,
                print_out=True,
            )
            if A_beats_B >= 0.5:
                new_tourney.append((teamA, seedA, A_beats_B * prA))
                if seedA > seedB:
                    print(f"\t{seedA} {seedB} UPSET")
            else:
                new_tourney.append((teamB, seedB, (1 - A_beats_B) * prB))
                if seedB > seedA:
                    print(f"\t{seedB} {seedA} UPSET")

        rounds.append(new_tourney)
        tourney = new_tourney

    print(tourney)
    return rounds


def virtual_tourney(year: int) -> list:
    """
    Given a year, rank the top NUM_TEAMS teams according to our ranking system.
    Arrange these teams based off this ranking into a NCAA bracket.
    Simulate the bracket, predicting each matchup and the outcome with some confidence.
    """

    NUM_TEAMS = 64
    NUM_SEEDS = 16
    SEED_COUNT = NUM_TEAMS // NUM_SEEDS

    try:
        rankings = sorted(
            pickle.load(open(f"./predictions/{year}_rankings.p", "rb")).items(),
            key=lambda x: -x[1],
        )[:NUM_TEAMS]

        for i in range(NUM_SEEDS):
            for j in range(SEED_COUNT):
                # (team_name, seed, probability of getting to current point)
                rankings[SEED_COUNT * i + j] = (
                    rankings[SEED_COUNT * i + j][0],
                    i + 1,
                    1,
                )

        tourney = build_tourney(rankings)
        return simulate_tourney(year, tourney)

    except FileNotFoundError:
        rank(year)
        return virtual_tourney(year)


year = 2021
teams = [
    "gonzaga",
    # "norfolk-state",
    # "oklahoma",
    # "missouri",
    "creighton",
    # "california-santa-barbara",
    # "virginia",
    # "ohio",
    "southern-california",
    # "drake",
    # "kansas",
    # "eastern-washington",
    "oregon",
    # "virginia-commonwealth",
    # "iowa",
    # "grand-canyon",
    "michigan",
    # "texas-southern",
    # "louisiana-state",
    # "st-bonaventure",
    # "colorado",
    # "georgetown",
    "florida-state",
    # "north-carolina-greensboro",
    # "brigham-young",
    "ucla",
    # "texas",
    # "abilene-christian",
    # "connecticut",
    # "maryland",
    "alabama",
    # "iona",
    "baylor",
    # "hartford",
    # "north-carolina",
    # "wisconsin",
    "villanova",
    # "winthrop",
    # "purdue",
    # "north-texas",
    # "texas-tech",
    # "utah-state",
    "arkansas",
    # "colgate",
    # "florida",
    # "virginia-tech",
    # "ohio-state",
    "oral-roberts",
    # "illinois",
    # "drexel",
    "loyola-il",
    # "georgia-tech",
    # "tennessee",
    "oregon-state",
    # "oklahoma-state",
    # "liberty",
    # "san-diego-state",
    "syracuse",
    # "west-virginia",
    # "morehead-state",
    # "clemson",
    # "rutgers",
    "houston",
    # "cleveland-state",
]
tourney = [(team, 1, 1) for team in teams]

rank(year, iters=10000)
simulate_tourney(year, tourney)
