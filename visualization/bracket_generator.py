import math

from comparison import Tournament, TeamComparator


def make_bracket(
    tournament: Tournament,
    comparator: TeamComparator,
    filename: str,
    whitespace_buffer: int = 1,
    entry_width: int = 4,
    title_height: int = 2,
):
    # Check that num_teams is a positive integer
    num_teams = len(tournament)
    if type(num_teams) is not int or num_teams <= 0:
        raise ValueError("Number of teams must be a positive integer")

    # Check that num_teams is a power of 2
    if num_teams & (num_teams - 1) != 0:
        raise ValueError("Number of teams must be a power of 2")

    total_depth = int(math.log2(num_teams))

    # Calculate size of bracket bounding rectangle
    total_width = 2 * entry_width * total_depth + 4 * whitespace_buffer
    total_height = num_teams // 2 + 2 * whitespace_buffer + title_height - 1
    bounding_x = total_width - whitespace_buffer
    bounding_y = total_height - whitespace_buffer
    # Calculating the maximum coordinates of the bracket becomes useful
    bracket_x = bounding_x - whitespace_buffer
    bracket_y = bounding_y

    # Create bracket by opening tikz file
    with open(filename, "w") as file:
        # Start tikz document
        file.writelines(
            [
                "\\documentclass[tikz]{standalone}\n\n",
                "\\usetikzlibrary{positioning}\n\n",
                "\\begin{document}\n",
                "\\begin{tikzpicture}\n",
            ],
        )

        # Draw bounding rectangle and title
        file.writelines(
            [
                f"\t\draw {-whitespace_buffer,-whitespace_buffer} rectangle {bounding_x,bounding_y};\n",
                f"\t\\node at {bracket_x/2,total_height-title_height-0.5} {{\Huge {comparator.__class__.__name__} Bracket}};\n",
            ]
        )

        # Draw Levels 0,...,depth-1
        # These levels also correspond to deeper rounds in the tournament
        for depth in range(total_depth):
            teams_remaining = len(tournament)

            # Coordinates for connecting look like: power_of_2*i + yp
            # These give the yp for adjacent teams and the average yp for drawing next level line
            yp_bottom = (2 ** (depth - 1) - 1) / 2
            yp_top = (3 * (2 ** (depth - 1)) - 1) / 2
            yp_mid = (yp_bottom + yp_top) / 2

            # X coordinates for creating left and right halves of bracket
            x_left = depth * entry_width
            x_right = bracket_x - depth * entry_width

            # # Count for enumerating entries in bracket
            # count = 2 * num_teams * (2**depth - 1) >> depth

            for i in range(num_teams >> (depth + 1)):
                # Y coordinates
                y_bottom = 2**depth * i + yp_bottom
                y_top = 2**depth * i + yp_top
                y_mid = 2**depth * i + yp_mid

                # Draw lines connecting adjacent pairs of teams
                # Don't have anything to connect from for the first level
                if depth > 0:
                    file.writelines(
                        [
                            f"\t\draw {x_left, y_bottom} to {x_left, y_top};\n",
                            f"\t\draw {x_right, y_bottom} to {x_right, y_top};\n",
                        ]
                    )

                # Draw lines for next level
                left_team = tournament[teams_remaining // 2 - i - 1]
                right_team = tournament[teams_remaining - i - 1]
                file.writelines(
                    [
                        f"\t\draw {x_left, y_mid} to node[above]{{({left_team.seed}) {left_team.name}}} {x_left + entry_width, y_mid};\n",
                        f"\t\draw {x_right, y_mid} to node[above]{{({right_team.seed}) {right_team.name}}} {x_right - entry_width, y_mid};\n",
                    ]
                )

            # Play a simulated round of the tournament, eliminating half the teams
            tournament.play_round(comparator)

        # Draw line for winner
        winner_y = bracket_y / 2 + 2 * whitespace_buffer
        winner_stetch = 1.5
        winning_team = tournament[0]
        file.write(
            f"\t\draw[thick] ({(bracket_x - winner_stetch*entry_width)/2},{winner_y}) to node[above]{{\Large {f'({winning_team.seed}) ' + winning_team.name}}} ({(bracket_x + winner_stetch*entry_width)/2},{winner_y});\n"
        )

        # End tikz document
        file.writelines(
            [
                "\\end{tikzpicture}\n",
                "\\end{document}\n",
            ]
        )
