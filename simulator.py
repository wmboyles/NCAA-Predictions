"""
This is the main script for the NCAA predictions project.
One can select a comparator to compare teams and simulate a tournament.
"""

from os import system
from datetime import datetime

from comparison import Tournament
from comparison.team_comparators import TeamComparator, COMPARATORS
from visualization.bracket_generator import make_bracket

tourney = Tournament.from_name_list([])


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
