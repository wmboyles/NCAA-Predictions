from math import log2
from os import system


def make_bracket(
    num_teams: int,
    filename: str,
    title: str,
    whitespace_buffer: int = 1,
    entry_width: int = 3,
    title_height: int = 2,
):
    # Check that num_teams is a power of 2
    if num_teams & (num_teams - 1) != 0:
        raise ValueError("Number of teams must be a power of 2")
    depth = int(log2(num_teams))

    # Calculate size of bracket bounding rectangle
    total_width = 2 * entry_width * depth + 4 * whitespace_buffer
    total_height = num_teams // 2 + 2 * whitespace_buffer - 1 + title_height
    bounding_x = total_width - whitespace_buffer
    bounding_y = total_height - whitespace_buffer
    # Calculating the maximum coordinates of the bracket becomes useful
    bracket_x = bounding_x - whitespace_buffer
    bracket_y = bounding_y

    # Create bracket by opening tikz file
    with open(filename, "w") as file:
        # Start tikz document
        file.write(
            r"""\documentclass[tikz]{standalone}

\usetikzlibrary{positioning}

\begin{document}
\begin{tikzpicture}
"""
        )

        # Draw bounding rectangle
        file.write(
            f"\t\draw (-{whitespace_buffer},-{whitespace_buffer}) rectangle ({bounding_x},{bounding_y});\n"
        )

        # Draw title
        file.write(
            f"\t\\node at ({bracket_x/2},{total_height-title_height-0.5}) {{\Huge {title}}};\n"
        )

        # Draw Levels 0,...,depth-1
        for j in range(depth):
            for i in range(num_teams >> (j + 1)):
                # Coordinates for connecting look like: power_of_2*i + yp
                # These give the yp for the first and second coordinates below
                yp1 = (2 ** (j - 1) - 1) / 2
                yp2 = (3 * (2 ** (j - 1)) - 1) / 2
                # Y coordinates
                y1 = 2**j * i + yp1
                y2 = 2**j * i + yp2
                y3 = (y1 + y2) / 2
                # X coordinates
                x1 = j * entry_width
                x2 = bracket_x - j * entry_width

                # Draw lines for next level
                count = 2 * num_teams * (2**j - 1) >> j
                file.write(
                    f"\t\draw ({x1},{y3}) to node[above]{{{count + 2*i}}} ({x1+entry_width},{y3});\n"
                )
                file.write(
                    f"\t\draw ({x2},{y3}) to node[above]{{{count + 2*i + 1}}} ({x2-entry_width},{y3});\n"
                )

                # Draw lines connecting adjacent pairs of teams
                if j > 0:
                    file.write(f"\t\draw ({x1},{y1}) to ({x1},{y2});\n")
                    file.write(f"\t\draw ({x2},{y1}) to ({x2},{y2});\n")

        # Draw line for winner
        winner_y = bracket_y / 2 + 2 * whitespace_buffer
        winner_stetch = 1.5
        file.write(
            f"\t\draw[thick] ({(bracket_x - winner_stetch*entry_width)/2},{winner_y}) to node[above]{{\Large {2*num_teams - 2}}} ({(bracket_x + winner_stetch*entry_width)/2},{winner_y});\n"
        )

        # End tikz document
        file.write(
            r"""\end{tikzpicture}
\end{document}
"""
        )


filename = "python_bracket.tex"
make_bracket(64, filename, "Enumerated Tournament")
system(f"xelatex {filename}")
system(f"start {filename[:-4]}.pdf")
