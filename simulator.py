import pickle

from team_comparators import PageRankComparator
from tournament import Tournament


def build_tourney(rankings: list) -> list:
    """
    Given a list of teams in ranked order, reorder them in NCAA bracket format.
    NCAA Bracket Format:
    1) In any list of teams of length L the #1 ranked team should play the #L ranked team in the first round
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
    comparator = PageRankComparator(year)

    rounds = [tourney]
    while len(tourney) > 1:
        print(tourney)
        print("--------------------------------------------------")

        new_tourney = []
        for i in range(0, len(tourney), 2):
            # team name, seed in bracket, model's probability that they advance to current position
            teamA, seedA, prA = tourney[i]
            teamB, seedB, prB = tourney[i + 1]

            A_beats_B = comparator.compare_teams(teamA, teamB)
            if A_beats_B >= 0.5:
                print(f"{teamA} beats {teamB} ({A_beats_B})")

                new_tourney.append((teamA, seedA, A_beats_B * prA))
                if seedA > seedB:
                    print(f"\t{seedA} {seedB} UPSET")
            else:
                print(f"{teamB} beats {teamA} ({1 - A_beats_B})")

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
        PageRankComparator(year)
        return virtual_tourney(year)


year = 2022
teams = [
    # Quadrant 1
    "gonzaga",
    "georgia-state",
    "boise-state",
    "memphis",
    "connecticut",
    "new-mexico-state",
    "arkansas",
    "vermont",
    "alabama",
    "rutgers",
    "texas-tech",
    "montana-state",
    "michigan-state",
    "davidson",
    "duke",
    "cal-state-fullerton",
    # Quadrant 2
    "baylor",
    "norfolk-state",
    "north-carolina",
    "marquette",
    "saint-marys-ca",
    "indiana",
    "ucla",
    "akron",
    "texas",
    "virginia-tech",
    "purdue",
    "yale",
    "murray-state",
    "san-francisco",
    "kentucky",
    "saint-peters",
    # Quadrant 3
    "arizona",
    "wright-state",
    "seton-hall",
    "texas-christian",
    "houston",
    "alabama-birmingham",
    "illinois",
    "chattanooga",
    "colorado-state",
    "michigan",
    "tennessee",
    "longwood",
    "ohio-state",
    "loyola-il",
    "villanova",
    "delaware",
    # Quadrant 4
    "kansas",
    "texas-southern",
    "san-diego-state",
    "creighton",
    "iowa",
    "richmond",
    "providence",
    "south-dakota-state",
    "louisiana-state",
    "iowa-state",
    "wisconsin",
    "colgate",
    "southern-california",
    "miami-fl",
    "auburn",
    "jacksonville-state",
]
tourney = Tournament(teams)
simulate_tourney(year, tourney)
