"""
Summarizes every game played by every D1 team in the given season into lists.
Each list entry is a list containing the opponent, whether the team won.ost (True/False), and the home/away team score.
This list of lists is then serialized into a "summary" file called  [TEAM_NAME]_summary.p.
"""

import csv
import pickle
import os

TEAM_NAME_REMOVE_CHARS = frozenset([".", "&", "(", ")", "'"])

def summarize_team_file(year: int, gender: str, dashed_team_name: str) -> list | None:
    """
    Summarizes a team's performance from a .csv file into just a list of the team's opponent and game score for each game.
    This list is then returned.
    """

    try:
        team_year_file = f"./games/{gender}/{year}/{dashed_team_name}_games.csv"
        with open(team_year_file, "r", newline="") as in_csv:
            reader = csv.reader(in_csv)

            # What is built and eventually returned
            new_rows = []

            for row in reader:
                # Skip empty rows
                if not row or not row[0]:
                    continue

                """
                Trying my best to format opponents the same way they are in the teams file.
                SportsReference sometimes uses different names for teams in the gamelog tables.
                This is meant to correct all division I teams.
                The team filename is meant to match the school URL on SportsReference.
                """

                opponent = row[3].lower()
                for char in TEAM_NAME_REMOVE_CHARS:
                    opponent = opponent.replace(char, "")
                opponent = opponent.replace("-", " ")

                # TODO: This is honestly awful and hard to maintain
                match opponent.split():
                    case ["unc", *rest]:
                        opponent = f"north carolina {' '.join(rest)}"
                    case ["uc", *rest]:
                        opponent = f"california {' '.join(rest)}"
                    case ["umass", *rest]:
                        opponent = f"massachusetts {' '.join(rest)}"
                match opponent:
                    case "nc state":
                        opponent = "north carolina state"
                    case "purdue fort wayne":
                        opponent = "ipfw"
                    case "texas rio grande valley":
                        opponent = "texas pan american"
                    case "omaha":
                        opponent = "nebraska omaha"
                    case "little rock":
                        opponent = "arkansas little rock"
                    case "louisiana":
                        opponent = "louisiana lafayette"
                    case "lsu":
                        opponent = "louisiana state"
                    case "usc":
                        opponent = "southern california"
                    case "usc upstate":
                        opponent = "south carolina upstate"
                    case "ole miss":
                        opponent = "mississippi"
                    case "unlv":
                        opponent = "nevada las vegas"
                    case "siu edwardsville":
                        opponent = "southern illinois edwardsville"
                    case "ut martin":
                        opponent = "tennessee martin"
                    case "ucf":
                        opponent = "central florida"
                    case "uconn":
                        opponent = "connecticut"
                    case "smu":
                        opponent = "southern methodist"
                    case "penn":
                        opponent = "pennsylvania"
                    case "vcu":
                        opponent = "virginia commonwealth"
                    case "umkc":
                        opponent = "missouri kansas city"
                    case "byu":
                        opponent = "brigham young"
                    case "uic":
                        opponent = "illinois chicago"
                    case "pitt":
                        opponent = "pittsburgh"
                    case "uncg":
                        opponent = "north carolina greensboro"
                    case "etsu":
                        opponent = "east tennessee state"
                    case "saint marys":
                        opponent = "saint marys ca"
                    case "utep":
                        opponent = "texas el paso"
                    case "ucsb":
                        opponent = "california santa barbara"
                    case "greensboro":
                        opponent = "north carolina greensboro"
                    case "central connecticut":
                        opponent = "central connecticut state"
                    case "umbc":
                        opponent = "maryland baltimore county"
                    case "st peters":
                        opponent = "saint peters"
                    case "st josephs":
                        opponent = "saint josephs"
                    case "st josephs ny":
                        opponent = "saint josephs"
                    case "central connecticut":
                        opponent = "central connecticut state"
                    case "uab":
                        opponent = "alabama birmingham"
                    case "utsa":
                        opponent = "texas san antonio"
                    case "unc greensboro":
                        opponent = "north carolina greensboro"
                    case "massachusetts boston":
                        opponent = "massachusetts"
                    case "tcu":
                        opponent = "texas christian"
                    case "southern miss":
                        opponent = "southern mississippi"
                    case "vmi":
                        opponent = "virginia military institute"
                    case "william  mary":
                        opponent = "william mary"
                    case "missouri st":
                        opponent = "missouri state"
                    case "detroit":
                        opponent = "detroit mercy"

                opponent = "-".join(opponent.strip().split(" "))

                """
                Calculate some basic stats for each game for each team.
                Below describes the format of each row in the table we're building for each team.
                A and B are team names

                [A, B, W/L, A_score, B_score, A_eFG%, B_eFG%, A_TOV%, B_TOV%, A_ORB%, B_ORB%, A_FTR, B_FTR]
                
                eFG% = (FG + .5*3P)/FGA
                TOV% = TOV / (FGA + .44*FTA + TOV)
                ORB% = ORB / (ORB + OppDRB)
                FTR = FT / FGA
                
                    game number = row[0]
                    date = row[1]
                    location = row[2] (blank for home, @ for away, N for neutral)
                A = dashed_team_name,   B = opponent (row[3])
                    type = row[4] (REG, conf/non-conf)
                    W/L = "W" in row[5]
                A_score = row[6],       B_score = row[7]
                    overtime = Value (OT etc.) in row[8]
                A_FG = row[9],          B_FG = row[30]
                A_FGA = row[10],        B_FGA = row[31] 
                A_FG% = row[11],        B_FG% = row[32]
                A_3P = row[12],         B_3P = row[33]
                A_3PA = row[13],        B_3PA = row[34]
                A_3P% = row[14],        B_3P% = row[35]
                A_2P = row[15],         B_2P = row[36]
                A_2PA = row[16],        B_2PA = row[37]
                A_2P% = row[17],        B_2P% = row[38]
                A_eFG% = row[18],       B_eFG% = row[39]
                A_FT = row[19],         B_FT = row[40]
                A_FTA = row[20],        B_FTA = row[41]
                A_FT% = row[21],        B_FT% = row[42]
                A_ORB = row[22],        B_ORB = row[43]
                A_DRB = row[23],        B_DRB = row[44]
                A_TRB = row[24],        B_TRB = row[45]
                A_AST = row[25],        B_AST = row[46]
                A_STL = row[26],        B_STL = row[47]
                A_BLK = row[27],        B_BLK = row[48]
                A_TOV = row[28],        B_TOV = row[49]
                A_PF = row[29],         A_PF = row[50]

                NOTE: After 2025, the SportsReference table schema changed
                """

                A, B = dashed_team_name, opponent
                WL = "W" in row[5]
                A_TO_B = 21 # A_stat = row[i], B_stat = row[i+A_TO_B]
                try:
                    A_SCORE, A_SCORE = int(row[6]), int(row[7])
                    A_FGA, B_FGA = int(row[10]), int(row[10+A_TO_B])
                    A_EFGP, B_EFGP = float(row[18]), float(row[18+A_TO_B])
                    A_FT, B_FT = int(row[19]), int(row[19+A_TO_B])
                    A_FTA, B_FTA = int(row[20]), int(row[20+A_TO_B])
                    A_ORB, B_ORB = int(row[22]), int(row[22+A_TO_B])
                    A_DRB, B_DRB = int(row[23]), int(row[23+A_TO_B])
                    A_TOV, B_TOV = int(row[28]), int(row[29+A_TO_B])

                    
                    A_TOVP = A_TOV / max(A_FGA + 0.44 * A_FTA + A_TOV, 1.0)
                    B_TOVP = B_TOV / max(B_FGA + 0.44 * B_FTA + B_TOV, 1.0)

                    A_ORBP = A_ORB / max(A_ORB + B_DRB, 1)
                    B_ORBP = B_ORB / max(B_ORB + A_DRB, 1)

                    A_FTR = A_FT / max(A_FGA, 1)
                    B_FTR = B_FT / max(B_FGA, 1)

                    new_row = [
                        A,
                        B,
                        WL,
                        A_SCORE,
                        A_SCORE,
                        A_EFGP,
                        B_EFGP,
                        A_TOVP,
                        B_TOVP,
                        A_ORBP,
                        B_ORBP,
                        A_FTR,
                        B_FTR,
                    ]
                    new_rows.append(new_row)
                except ValueError:
                    print(
                        f"--- WARNING: {dashed_team_name} vs. {opponent} {year} missing values"
                    )
                    continue

        return new_rows
    except FileNotFoundError:
        print(f"--- WARNING: {dashed_team_name} games not found.")


def summarize_team_files(
    year: int,
    gender: str,
    teamFile: str = "../teams/teams.txt",
):
    """
    Summarizes all teams in a given file listing teams.
    The list returned from the summarize_team_file method is serialized into a .p file corresponding to the team's name in the summaries folder.
    """

    with open(teamFile, "r") as teams:
        for team in teams:
            # Don't include last character b/c it's a \n
            fmt_team = "-".join(team[:-1].split(" "))
            print(f"Summarizing {fmt_team} {year}")

            summary = summarize_team_file(year, gender, fmt_team)
            if summary is None or len(summary) == 0:
                print(f"----WARNING: {fmt_team} does not have a game summary.")
                continue

            # Make the year folder
            outfile = f"./summaries/{gender}/{year}/{fmt_team}_summary.p"
            os.makedirs(os.path.dirname(outfile), exist_ok=True)

            pickle.dump(summary, open(outfile, "wb"))


def combine_summaries(year: int, gender: str, teamFile: str = "../teams/teams.txt"):
    """
    Combines all summary files into a large summary to be read by the ranker program.
    """

    big_summary = []

    with open(teamFile, "r") as teams:
        for team in teams:
            fmt_team = "-".join(team[:-1].split(" "))
            print(f"Combining {fmt_team}")

            try:
                team_summary = pickle.load(
                    open(f"./summaries/{gender}/{year}/{fmt_team}_summary.p", "rb")
                )

                for summary_entry in team_summary:
                    big_summary.append(summary_entry)

            except FileNotFoundError:
                print(f"----WARNING: {fmt_team} does not have a summary file")
                continue

    pickle.dump(big_summary, open(f"./summaries/{gender}/{year}/total_summary.p", "wb"))
