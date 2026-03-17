"""
This is the main script for the NCAA predictions project.
One can select a comparator to compare teams and simulate a tournament.
"""

from os import system
from datetime import datetime

from comparison import Tournament
from comparison.team_comparators import TeamComparator
from visualization.bracket_generator import make_bracket

# Seeds: [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
tourney_men = Tournament.from_name_list(
    [
        # South
        "florida",
        "prairie-view", # or lehigh
        "clemson",
        "iowa",
        "nebraska",
        "troy",
        "vanderbilt",
        "mcneese-state",
        "houston",
        "idaho",
        "saint-marys-ca",
        "texas-am",
        "illinois",
        "penn-state",
        "north-carolina",
        "virginia-commonwealth",
        # West
        "arizona",
        "long-island-university",
        "villanova",
        "utah-state",
        "arkansas",
        "hawaii",
        "wisconsin",
        "high-point",
        "purdue",
        "queens-nc",
        "miami-fl",
        "missouri",
        "gonzaga",
        "kennesaw-state",
        "brigham-young",
        "north-carolina-state", # or texas
        # East
        "duke",
        "siena",
        "ohio-state",
        "texas-christian",
        "kansas",
        "california-baptist",
        "st-johns-ny",
        "northern-iowa",
        "connecticut",
        "furman",
        "ucla",
        "central-florida",
        "michigan-state",
        "north-dakota-state",
        "louisville",
        "south-florida",
        # Midwest
        "michigan",
        "maryland-baltimore-county", # or howard
        "georgia",
        "saint-louis",
        "alabama",
        "hofstra",
        "texas-tech",
        "akron",
        "iowa-state",
        "tennessee-state",
        "kentucky",
        "santa-clara",
        "virginia",
        "wright-state",
        "tennessee",
        "southern-methodist" # or miami-oh
    ]
)

tourney_dict: dict[str, Tournament] = {"men": tourney_men}


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
    system(f"md predictions")
    for extension in ["log", "aux"]:
        system(f"del {filename}.{extension}")
    for extension in ["tex", "pdf"]:
        system(f"move {filename}.{extension} ./predictions/")

    system(f"start ./predictions/{filename}.pdf")


if __name__ == "__main__":
    from comparison.team_comparators import *

    year = datetime.now().year
    gender = "men"
    comp = ResistanceComparator(year, gender)
    tourney = tourney_dict[gender]
    main(tourney, year, gender, comp)
