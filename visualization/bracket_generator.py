import math
from os import system


def make_bracket(
    num_teams: int,
    filename: str,
    title: str,
    whitespace_buffer: int = 1,
    entry_width: int = 3,
    title_height: int = 2,
):
    # Check that num_teams is a positive integer
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
                f"\t\\node at {bracket_x/2,total_height-title_height-0.5} {{\Huge {title}}};\n",
            ]
        )

        # Draw Levels 0,...,depth-1
        for depth in range(total_depth):
            # Coordinates for connecting look like: power_of_2*i + yp
            # These give the yp for adjacent teams and the average yp for drawing next level line
            yp_bottom = (2 ** (depth - 1) - 1) / 2
            yp_top = (3 * (2 ** (depth - 1)) - 1) / 2
            yp_mid = (yp_bottom + yp_top) / 2

            # X coordinates for creating left and right halves of bracket
            x_left = depth * entry_width
            x_right = bracket_x - depth * entry_width

            # Count for enumerating entries in bracket
            count = 2 * num_teams * (2**depth - 1) >> depth

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
                file.writelines(
                    [
                        f"\t\draw {x_left, y_mid} to node[above]{{{count + 2*i}}} {x_left + entry_width, y_mid};\n",
                        f"\t\draw {x_right, y_mid} to node[above]{{{count + 2*i + 1}}} {x_right - entry_width, y_mid};\n",
                    ]
                )

        # Draw line for winner
        winner_y = bracket_y / 2 + 2 * whitespace_buffer
        winner_stetch = 1.5
        file.write(
            f"\t\draw[thick] ({(bracket_x - winner_stetch*entry_width)/2},{winner_y}) to node[above]{{\Large {2*num_teams - 2}}} ({(bracket_x + winner_stetch*entry_width)/2},{winner_y});\n"
        )

        # End tikz document
        file.writelines(
            [
                "\\end{tikzpicture}\n",
                "\\end{document}\n",
            ]
        )


filename = "python_bracket.tex"
make_bracket(64, filename, "Enumerated Tournament")
system(f"xelatex {filename}")
system(f"start {filename[:-4]}.pdf")
