"""
Summarizes every game played by every D1 team in the given season into lists.
Each list entry is a list containing the opponent, whether the team won.ost (True/False), and the home/away team score.
This list of lists is then serialized into a "summary" file called  [TEAM_NAME]_summary.p.
"""

import csv
import pickle
import os


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

                opponent = row[2].lower()
                for char in [".", "&", "(", ")", "'"]:
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
                
                A = dashed_team_name,   B = opponent
                W/L = "W" in row[3]
                A_score = row[4],       B_score = row[5]
                A_FG = row[6],          B_FG = row[23]
                A_FGA = row[7],         B_FGA = row[24] 
                A_3P = row[9],          B_3P = row[26]
                A_TOV = row[20],        B_TOV = row[37]
                A_FTA = row[13],        B_FTA = row[30]
                A_ORB = row[15],        B_ORB = row[32]
                A_FT = row[12],         B_FT = row[29]
                """

                A, B = dashed_team_name, opponent
                WL = "W" in row[3]
                try:
                    A_score, B_score = int(row[4]), int(row[5])
                    A_FG, B_FG = int(row[6]), int(row[23])
                    A_FGA, B_FGA = int(row[7]), int(row[24])
                    A_3P, B_3P = int(row[9]), int(row[26])
                    A_TOV, B_TOV = int(row[20]), int(row[37])
                    A_FTA, B_FTA = int(row[13]), int(row[30])
                    A_ORB, B_ORB = int(row[15]), int(row[32])
                    A_FT, B_FT = int(row[12]), int(row[29])

                    if A_FGA == 0:
                        A_eFGp = 0
                    else:
                        A_eFGp = (A_FG + 0.5 * A_3P) / A_FGA
                    if B_FGA == 0:
                        B_eFGp = 0
                    else:
                        B_eFGp = (B_FG + 0.5 * B_3P) / B_FGA

                    if A_FGA == 0 and A_FTA == 0 and A_TOV == 0:
                        A_TOVp = 0
                    else:
                        A_TOVp = A_TOV / (A_FGA + 0.44 * A_FTA + A_TOV)
                    if B_FGA == 0 and B_FTA == 0 and B_TOV == 0:
                        B_TOVp = 0
                    else:
                        B_TOVp = B_TOV / (B_FGA + 0.44 * B_FTA + B_TOV)

                    if A_ORB == 0 and B_ORB == 0:
                        A_ORBp, B_ORBp = 0, 0
                    else:
                        A_ORBp, B_ORBp = A_ORB / (A_ORB + B_ORB), B_ORB / (
                            A_ORB + B_ORB
                        )

                    if A_FTA == 0:
                        A_FTR = 0
                    else:
                        A_FTR = A_FT / A_FGA
                    if B_FTA == 0:
                        B_FTR = 0
                    else:
                        B_FTR = B_FT / B_FGA

                    new_row = [
                        A,
                        B,
                        WL,
                        A_score,
                        B_score,
                        A_eFGp,
                        B_eFGp,
                        A_TOVp,
                        B_TOVp,
                        A_ORBp,
                        B_ORBp,
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
