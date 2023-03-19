"""
This is the main script for the NCAA predictions project.
One can select a comparator to compare teams and simulate a tournament.
"""

from os import system
from datetime import datetime

from comparison import Tournament
from comparison.team_comparators import TeamComparator, COMPARATORS
from visualization.bracket_generator import make_bracket

# Seeds: [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
tourney_men = Tournament.from_name_list(
    [
        # South
        "alabama",
        "texas-am-corpus-christi",
        "maryland",
        "west-virginia",
        "virginia",
        "furman",
        "san-diego-state",
        "college-of-charleston",
        "arizona",
        "princeton",
        "missouri",
        "utah-state",
        "baylor",
        "california-santa-barbara",
        "creighton",
        "north-carolina-state",
        # East
        "purdue",
        "fairleigh-dickinson",  # play in vs texas-southern
        "memphis",
        "florida-atlantic",
        "tennessee",
        "louisiana-lafayette",
        "duke",
        "oral-roberts",
        "marquette",
        "vermont",
        "michigan-state",
        "southern-california",
        "kansas-state",
        "montana-state",
        "kentucky",
        "providence",
        # Midwest
        "houston",
        "northern-kentucky",
        "iowa",
        "auburn",
        "indiana",
        "kent-state",
        "miami-fl",
        "drake",
        "texas",
        "colgate",
        "texas-am",
        "penn-state",
        "xavier",
        "kennesaw-state",
        "iowa-state",
        "pittsburgh",
        # West
        "kansas",
        "howard",
        "arkansas",
        "illinois",
        "connecticut",
        "iona",
        "saint-marys-ca",
        "virginia-commonwealth",
        "ucla",
        "north-carolina-asheville",
        "northwestern",
        "boise-state",
        "gonzaga",
        "grand-canyon",
        "texas-christian",
        "arizona-state",  # play in vs nevada
    ]
)

tourney_women = Tournament.from_name_list(
    [
        # Greenville 1
        "south-carolina",
        "norfolk-state",
        "south-florida",
        "marquette",
        "ucla",
        "sacramento-state",
        "oklahoma",
        "portland",
        "maryland",
        "holy-cross",
        "arizona",
        "west-virginia",
        "notre-dame",
        "southern-utah",
        "creighton",
        "mississippi-state",
        # Seattle 4
        "stanford",
        "sacred-heart",
        "mississippi",
        "gonzaga",
        "texas",
        "east-carolina",
        "louisville",
        "drake",
        "iowa",
        "southeastern-louisiana",
        "florida-state",
        "georgia",
        "duke",
        "iona",
        "colorado",
        "middle-tennessee",
        # Greenville 2
        "indiana",
        "tennessee-tech",
        "oklahoma-state",
        "miami-fl",
        "villanova",
        "cleveland-state",
        "washington-state",
        "florida-gulf-coast",
        "utah",
        "gardner-webb",
        "north-carolina-state",
        "princeton",
        "louisiana-lafayette",
        "hawaii",
        "michigan",
        "nevada-las-vegas",
        # Seattle 3
        "virginia-tech",
        "chattanooga",
        "southern-california",
        "south-dakota-state",
        "tennessee",
        "saint-louis",
        "iowa-state",
        "toledo",
        "connecticut",
        "vermont",
        "baylor",
        "alabama",
        "ohio-state",
        "james-madison",
        "north-carolina",
        "st-johns-ny"
    ]
)


def main(tourney: Tournament, year: int, gender: str, comparator: TeamComparator):
    comparator_name = comparator.__class__.__name__

    filename = f"{comparator_name}-{gender}-{year}"
    full_filename = f"{filename}.tex"

    make_bracket(
        tourney,
        comparator,
        filename=full_filename,
        title=f"{comparator_name} {gender} {year}",
    )

    system(f"xelatex {full_filename} -interaction batchmode")

    for extension in ["log", "aux"]:
        system(f"del {filename}.{extension}")
    for extension in ["tex", "pdf"]:
        system(f"move {filename}.{extension} ./predictions/")

    system(f"start ./predictions/{filename}.pdf")


if __name__ == "__main__":
    from comparison.team_comparators import *

    year = datetime.now().year
    gender = "women"
    comp = PageRankComparator(year, gender)
    main(tourney_women, year, gender, comp)