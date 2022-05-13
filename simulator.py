"""
This is the main script for the NCAA predictions project.
One can select a comparator to compare teams and simulate a tournament.
"""
from os import system

import comparison
from visualization.bracket_generator import make_bracket


tourney = comparison.Tournament(
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

year = 2022
filename = "python_bracket.tex"
comparator = comparison.team_comparators.PageRankComparator(year)

make_bracket(tourney, comparator, filename=filename)
system(f"xelatex {filename}")
system(f"rm {filename[:-4]}.log {filename[:-4]}.aux")
system(f"start {filename[:-4]}.pdf")
