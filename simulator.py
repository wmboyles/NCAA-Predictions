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
tourney = Tournament.from_name_list(
    [
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
        # South
        "alabama",
        "southeast-missouri-state",  # play in vs texas-am-corpus-christi
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
        "pittsburgh",  # play in vs mississippi-state
    ]
)


def main(year: int, comparator_type):
    comparator: TeamComparator = comparator_type.__call__(year=year)
    comparator_name = comparator.__class__.__name__

    filename = f"{comparator_name}-{year}"
    full_filename = f"{filename}.tex"

    make_bracket(
        tourney, comparator, filename=full_filename, title=f"{comparator_name} {year}"
    )

    system(f"xelatex {full_filename} -interaction batchmode")

    for extension in ["log", "aux"]:
        system(f"del {filename}.{extension}")
    for extension in ["tex", "pdf"]:
        system(f"move {filename}.{extension} ./predictions/viz/")

    system(f"start ./predictions/viz/{filename}.pdf")


if __name__ == "__main__":
    for comparator in COMPARATORS:
        main(datetime.now().year, comparator)
