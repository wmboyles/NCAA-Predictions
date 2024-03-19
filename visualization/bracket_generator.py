from math import log2
from functools import reduce
from collections import defaultdict

from comparison import Tournament, TeamComparator, Team


def make_bracket(tournament: Tournament, comparator: TeamComparator, **kwargs):
    """
    Draw a filled-in bracket in LaTeX using the TikZ library.
    Compile the LaTeX file to a PDF and view the bracket.

    kwargs:
        filename: Name of the file to write the LaTeX code to.
            Defaults to the name of the comparator class.
        title: Title of the bracket.
            Defaults to the name of the comparator class.
        whitespace_buffer: Amount of whitespace to leave around the bracket.
            Defaults to 1.
        entry_width: Horizontal width of each entry in the bracket.
            Defaults to 4.5.
        title_height: Height of the title of the bracket.
            Defaults to 2.

    TODO: Separate out comparator and drawing logic by using a BracketDrawer class.
    """

    game_tourney = tournament

    num_teams = len(game_tourney)
    if num_teams <= 0:
        raise ValueError("Number of teams must be a positive integer")
    if num_teams & (num_teams - 1) != 0:
        raise ValueError("Number of teams must be a power of 2")

    comparator_class_name = comparator.__class__.__name__
    default_kwargs = {
        "filename": f"{comparator_class_name}.tex",
        "title": f"{comparator_class_name} Bracket",
        "whitespace_buffer": 1,
        "entry_width": 4.5,
        "title_height": 2,
    }
    default_kwargs.update(kwargs)

    filename = default_kwargs["filename"]
    title = default_kwargs["title"]
    whitespace_buffer = default_kwargs["whitespace_buffer"]
    entry_width = default_kwargs["entry_width"]
    title_height = default_kwargs["title_height"]

    total_depth = int(log2(num_teams))

    # Calculate size of bracket bounding rectangle
    total_width = 2 * entry_width * total_depth + 4 * whitespace_buffer
    total_height = num_teams // 2 + 2 * whitespace_buffer + 2 * title_height - 1
    bounding_x = total_width - whitespace_buffer
    bounding_y = total_height - whitespace_buffer
    # Calculating the maximum coordinates of the bracket becomes useful
    bracket_x = bounding_x - whitespace_buffer
    bracket_y = bounding_y

    # Play successive tournament rounds until there is 1 winner
    rounds = [game_tourney]
    while len(rounds[-1]) > 1:
        rounds.append(rounds[-1].play_round(comparator=comparator))

    with open(filename, "w") as file:
        file.writelines(
            [
                # Start tikz document
                "\\documentclass[tikz]{standalone}\n\n",
                "\\usepackage{longtable}\n",
                "\\usetikzlibrary{positioning}\n\n",
                "\\begin{document}\n",
                "\\begin{tikzpicture}\n",
                # Draw bounding rectangle and title
                f"\t\draw {-whitespace_buffer,-whitespace_buffer} rectangle {bounding_x,bounding_y};\n",
                f"\t\\node at {bracket_x/2,total_height-title_height-0.5} {{\\fontsize{{50}}{{60}}\\selectfont \\underline{{{title}}}}};\n",
            ]
        )

        for depth, round in enumerate(rounds):
            teams_remaining = len(round)
            print("-" * 20 + f"Round of {teams_remaining}" + "-" * 20)

            # Coordinates for connecting look like: power_of_2*i + yp
            # These give the yp for adjacent teams and the average yp for drawing next level line
            yp_bottom = ((2 ** (depth - 1)) - 1) / 2
            yp_top = (3 * (2 ** (depth - 1)) - 1) / 2
            yp_mid = (yp_bottom + yp_top) / 2

            # X coordinates for creating left and right halves of bracket
            x_left = depth * entry_width
            x_right = bracket_x - depth * entry_width

            round_winners = round.round_winners()
            for i in range(teams_remaining // 2):
                # Y coordinates
                y_bottom = 2**depth * i + yp_bottom
                y_top = 2**depth * i + yp_top
                y_mid = 2**depth * i + yp_mid

                # Draw lines connecting adjacent pairs of teams
                # Don't have anything to connect from for the first level
                if depth > 0:
                    file.writelines(
                        [
                            f"\t\draw {x_left, y_bottom} to {x_left, y_top};\n"
                            f"\t\draw {x_right, y_bottom} to {x_right, y_top};\n"
                        ]
                    )

                # Draw lines for next level
                # TODO: This can create a weird outcome where a previously eliminated team is predicted to win
                left_team = round_winners[teams_remaining // 2 - i - 1]
                right_team = round_winners[teams_remaining - i - 1]
                file.writelines(
                    [
                        f"\t\draw {x_left, y_mid} to node[above]{{({left_team.seed}) {left_team.name}}} {x_left + entry_width, y_mid};\n",
                        f"\t\draw {x_right, y_mid} to node[above]{{({right_team.seed}) {right_team.name}}} {x_right - entry_width, y_mid};\n",
                    ]
                )

        # Draw line for winner and end document
        winner_y = y_mid + 2 * whitespace_buffer
        winner_stetch = 1.5
        winning_team = round.round_winners()[0]
        file.writelines(
            [
                f"\t\draw[thick] ({(bracket_x - winner_stetch*entry_width)/2},{winner_y}) to node[above]{{\Huge \\bf {{({winning_team.seed}) {winning_team.name}}}}} ({(bracket_x + winner_stetch*entry_width)/2},{winner_y});\n"
                "\\end{tikzpicture}\n"
            ]
        )

        # ----- Table -----
        file.writelines([
            "\Huge\n",
            "\\newpage\n",
            "\\begin{longtable}{| l ||" + " c |"*(total_depth+1) + "}\n",
            "\hline\n"
        ])

        table_header = "\\textbf{Team/Chances} "
        round_size = num_teams
        while round_size > 0:
            table_header += f"& \\textbf{{Round of {round_size}}}"
            round_size //= 2
        table_header += " \\\\\n"
        file.writelines([table_header, "\hline\hline\n"])

        # As list of list of GameResults. This might be easier for filling the bracket
        # TODO: Use this to fill bracket
        results = [round._leaves() for round in rounds]
        # As list of dict[Team,float], mapping Team to chances of making it to current round
        results2 = [
            reduce(lambda acc, r: acc | r.probabilities, leaves, dict[Team, float]())
            for leaves in results
        ]
        out = defaultdict[Team,list[float]](list)
        for r2 in results2:
            for t,p in r2.items():
                out[t].append(p)
        out = sorted(out.items(), key = lambda e: -e[1][-1])

        for i,(team,prs) in enumerate(out):
            line = f"\\textbf{{({team.seed}) {team.name}}} "
            for pr in prs:
                line += f"& {100*pr:0.3f}\% "
            line += "\\\\ \\hline\n"
            file.write(line)

            # Break table onto multiple pages if needed
            if (i+1) % (num_teams // 2) == 0 and (i+1) != num_teams:
                file.writelines([
                    "\pagebreak\n",
                    "\hline\n",
                    table_header, 
                    "\hline\hline\n"
                ])

        file.writelines(
            [
            "\\end{longtable}\n",
            "\\end{document}\n",
            ]
        )
