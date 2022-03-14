import pickle

from comparison.team_comparators import PageRankComparator
from comparison.tournament import Tournament


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
comparator = PageRankComparator(year)
tourney = Tournament(
    [
        #
        # Quadrant 1
        #
        "gonzaga",  # 1
        "georgia-state",  # 16
        "boise-state",  # 8
        "memphis",  # 9
        "arkansas",  # 4
        "vermont",  # 13
        "connecticut",  # 5
        "new-mexico-state",  # 12
        "duke",  # 2
        "cal-state-fullerton",  # 15
        "michigan-state",  # 7
        "davidson",  # 10
        "texas-tech",  # 3
        "montana-state",  # 14
        "alabama",  # 6
        "rutgers",  # 11
        #
        # Quadrant 2
        #
        "baylor",  # 1
        "norfolk-state",  # 16
        "north-carolina",  # 8
        "marquette",  # 9
        "ucla",  # 4
        "akron",  # 13
        "saint-marys-ca",  # 5
        "indiana",  # 12
        "kentucky",  # 2
        "saint-peters",  # 15
        "murray-state",  # 7
        "san-francisco",  # 10
        "purdue",  # 3
        "yale",  # 14
        "texas",  # 6
        "virginia-tech",  # 11
        #
        # Quadrant 3
        #
        "arizona",  # 1
        "wright-state",  # 16
        "seton-hall",  # 8
        "texas-christian",  # 9
        "illinois",  # 4
        "chattanooga",  # 13
        "houston",  # 5
        "alabama-birmingham",  # 12
        "villanova",  # 2
        "delaware",  # 15
        "ohio-state",  # 7
        "loyola-il",  # 10
        "tennessee",  # 3
        "longwood",  # 14
        "colorado-state",  # 6
        "michigan",  # 11
        #
        # Quadrant 4
        #
        "kansas",  # 1
        "texas-southern",  # 16
        "san-diego-state",  # 8
        "creighton",  # 9
        "providence",  # 4
        "south-dakota-state",  # 13
        "iowa",  # 5
        "richmond",  # 12
        "auburn",  # 2
        "jacksonville-state",  # 15
        "southern-california",  # 7
        "miami-fl",  # 10
        "wisconsin",  # 3
        "colgate",  # 14
        "louisiana-state",  # 6
        "iowa-state",  # 11
    ]
)
tourney.simulate(comparator)
