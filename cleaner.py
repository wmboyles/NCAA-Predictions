"""
Summarizes every game played by every D1 team in the given season
into a lists, where each list entry is a list containing the opponent, whether
the team won (True) or lost (False), the home team score, and the away team 
score.
This list of lists is then serialized into a "summary" file called 
[TEAM_NAME]_summary.p.
"""

import csv
import pickle
import os


def summarize_team_file(year, dashed_team_name):
    """
    Summarizes a team's performance from a .csv file into just a list of the team's
    opponent and game score for each game. This list is then returned.
    """

    try:
        with open(
            "./games/" + str(year) + "/" + dashed_team_name + "_games.csv",
            "r",
            newline="",
        ) as in_csv:
            reader = csv.reader(in_csv)

            new_rows = []  # What is built and eventually returned
            for row in reader:
                if len(row) == 0 or len(row[0]) == 0:
                    continue

                """
                Trying my best to format opponents the same way they are in the
                teams file. SportsReference sometimes uses different names for 
                teams in the gamelog tables. This is meant to correct all 
                division I teams. The team filename is meant to match the school 
                URL on SportsReference.
                """
                opponent = (
                    row[2]
                    .lower()
                    .replace(".", "")
                    .replace("&", "")
                    .replace("-", " ")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("'", "")
                )
                if opponent == "unc":
                    opponent = "north carolina"
                elif opponent == "unc asheville":
                    opponent = "north carolina asheville"
                elif opponent == "unc wilmington":
                    opponent = "north carolina wilmington"
                elif opponent == "nc state":
                    opponent = "north carolina state"
                elif opponent == "uc davis":
                    opponent = "california davis"
                elif opponent == "uc riverside":
                    opponent = "california riverside"
                elif opponent == "uc santa barbara":
                    opponent = "california santa barbara"
                elif opponent == "uc irvine":
                    opponent = "california irvine"
                elif opponent == "purdue fort wayne":
                    opponent = "ipfw"
                elif opponent == "texas rio grande valley":
                    opponent = "texas pan american"
                elif opponent == "omaha":
                    opponent = "nebraska omaha"
                elif opponent == "little rock":
                    opponent = "arkansas little rock"
                elif opponent == "louisiana":
                    opponent = "louisiana lafayette"
                elif opponent == "lsu":
                    opponent = "louisiana state"
                elif opponent == "usc":
                    opponent = "southern california"
                elif opponent == "usc upstate":
                    opponent = "south carolina upstate"
                elif opponent == "ole miss":
                    opponent = "mississippi"
                elif opponent == "unlv":
                    opponent = "nevada las vegas"
                elif opponent == "siu edwardsville":
                    opponent = "southern illinois edwardsville"
                elif opponent == "ut martin":
                    opponent = "tennessee martin"
                elif opponent == "ucf":
                    opponent = "central florida"
                elif opponent == "uconn":
                    opponent = "connecticut"
                elif opponent == "smu":
                    opponent = "southern methodist"
                elif opponent == "umass":
                    opponent = "massachusetts"
                elif opponent == "umass lowell":
                    opponent = "massachusetts lowell"
                elif opponent == "penn":
                    opponent = "pennsylvania"
                elif opponent == "vcu":
                    opponent = "virginia commonwealth"
                elif opponent == "umkc":
                    opponent = "missouri kansas city"
                elif opponent == "byu":
                    opponent = "brigham young"
                elif opponent == "uic":
                    opponent = "illinois chicago"
                elif opponent == "pitt":
                    opponent = "pittsburgh"
                elif opponent == "uncg":
                    opponent = "north carolina greensboro"
                elif opponent == "etsu":
                    opponent = "east tennessee state"
                elif opponent == "saint marys":
                    opponent = "saint marys ca"
                elif opponent == "utep":
                    opponent = "texas el paso"
                elif opponent == "ucsb":
                    opponent = "california santa barbara"
                elif opponent == "greensboro":
                    opponent = "north carolina greensboro"
                elif opponent == "central connecticut":
                    opponent = "central connecticut state"
                elif opponent == "umbc":
                    opponent = "maryland baltimore county"
                elif opponent == "st peters":
                    opponent = "saint peters"
                elif opponent == "st josephs":
                    opponent = "saint josephs"
                elif opponent == "st josephs ny":
                    opponent = "saint josephs"
                elif opponent == "central connecticut":
                    opponent = "central connecticut state"
                elif opponent == "utsa":
                    opponent = "texas san antonio"
                elif opponent == "unc greensboro":
                    opponent = "north carolina greensboro"
                elif opponent == "massachusetts boston":
                    opponent = "massachusetts"
                elif opponent == "tcu":
                    opponent = "texas christian"
                elif opponent == "southern miss":
                    opponent = "southern mississippi"
                elif opponent == "vmi":
                    opponent = "virginia military institute"
                elif opponent == "william  mary":
                    opponent = "william mary"
                elif opponent == "missouri st":
                    opponent = "missouri state"
                elif opponent == "detroit":
                    opponent = "detroit mercy"
                opponent = "-".join(opponent.split(" "))

                """
                A and B are team names
                [A, B, W/L, A_score, B_score, A_eFG%, B_eFG%, A_TOV%, B_TOV%, A_ORB%, B_ORB%, A_FTR, B_FTR]
                eFG% = (FG + .5*3P)/FGA
                TOV% = TOV / (FGA + .44*FTA + TOV)
                ORB% = ORB / (ORB + OppDRB)
                FTR = FT / FGA
                ------------------------
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
                        A_FTR = A_FT / A_FTA
                    if B_FTA == 0:
                        B_FTR = 0
                    else:
                        B_FTR = B_FT / B_FTA

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
                        "--- WARNING:",
                        dashed_team_name,
                        opponent,
                        year,
                        "missing values",
                    )
                    continue

        return new_rows
    except FileNotFoundError:
        print("--- WARNING:", dashed_team_name, "games not found.")
        return


def summarize_team_files(year=2019, teamFile="./teams/teams.txt"):
    """
    Summarizes all teams in a given file listing teams. The list returned from
    summarize_team_file is serialized into a .p file corresponding to the team's
    name in the summaries folder.
    """

    with open(teamFile, "r") as teams:
        for team in teams:
            # Don't include last character b/c it's a \n
            fmt_team = "-".join(team[:-1].split(" "))
            print("Summarizing", fmt_team, year)

            summary = summarize_team_file(year, fmt_team)
            if summary is None or len(summary) == 0:
                print("----WARNING:", fmt_team, "does not have a game summary.")
                continue

            # Make the year folder
            outfile = "./summaries/" + str(year) + "/" + fmt_team + "_summary.p"
            os.makedirs(os.path.dirname(outfile), exist_ok=True)

            pickle.dump(summary, open(outfile, "wb"))


def combine_summaries(year, teamFile="./teams/teams.txt"):
    """
    Combines all summary files into a large summary to be read by the ranker
    program.
    """

    big_summary = []

    with open(teamFile, "r") as teams:
        for team in teams:
            fmt_team = "-".join(team[:-1].split(" "))
            print("Combining", fmt_team)

            try:
                team_summary = pickle.load(
                    open(
                        "./summaries/" + str(year) + "/" + fmt_team + "_summary.p", "rb"
                    )
                )
                for summary_entry in team_summary:
                    big_summary.append(summary_entry)
            except FileNotFoundError:
                print("----WARNING:", fmt_team, "does not have a summary file")
                continue

    pickle.dump(
        big_summary, open("./summaries/" + str(year) + "/total_summary.p", "wb")
    )
