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
        "auburn",
        "alabama",  # or Saint Francis
        "louisville",
        "creighton",
        "texas-am",
        "yale",
        "michigan",
        "california-san-diego",  # TODO: UC San Diego
        "michigan-state",
        "bryant",
        "marquette",
        "new-mexico",
        "iowa-state",
        "lipscomb",
        "ole-miss",
        "san-diego-state",  # or North Carolina
        # West
        "florida",
        "norfolk-state",
        "connecticut",
        "oklahoma",
        "maryland",
        "grand-canyon",
        "memphis",
        "colorado-state",
        "st-johns-ny",
        "omaha",
        "kansas",
        "arkansas",
        "texas-tech",
        "north-carolina-wilmington",
        "missouri",
        "drake",
        # East
        "duke",
        "american",  # or mount st marys
        "mississippi-state",
        "baylor",
        "arizona",
        "akron",
        "oregon",
        "liberty",
        "alabama",
        "robert-morris",
        "saint-marys-ca",
        "vanderbilt",
        "wisconsin",
        "montana",
        "brigham-young",
        "virgina-commonwealth",
        # Midwest
        "houston",
        "southern-ilinois-edwardsville",
        "gonzaga",
        "georgia",
        "purdue",
        "high-point",
        "clemson",
        "mcnessee-state",
        "tennessee",
        "wofford",
        "ucla",
        "utah-state",
        "kentucky",
        "troy",
        "texas",  # or xavier
        "illinois",
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
    comp = EloComparator(year, gender)
    tourney = tourney_dict[gender]
    main(tourney, year, gender, comp)
