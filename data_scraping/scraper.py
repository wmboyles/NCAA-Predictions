"""
Gets a history of all games played by all division I NCAA basketball teams in a given season.
For each team listed in the file ./teams/teams.txt, this script makes a request to SportsReference.com for 2019 gamelogs.
This information is then parsed and written to a csv file called ./games/[TEAM_NAME]_games.csv.
This csv file is in the correct format to be read by cleaner.py.
"""

import requests
import bs4
import csv
import os
from time import sleep


def get_team_file(fmt_team: str, year: int, gender: str):
    """
    Request gamelogs from SportsReference.com given a dashed and formatted
    school name as described in get_team_files. Writes the information in the
    gamelog table to a .csv file saved under the team's name.
    """

    outfile = f"./games/{gender}/{year}/{fmt_team}_games.csv"

    if os.path.exists(outfile):
        print(f"Found gamelogs for {fmt_team} {gender} {year}.")
        return

    # format the url to the specific team and year
    # TODO: Women's teams?
    url = f"https://www.sports-reference.com/cbb/schools/{fmt_team}/{gender}/{year}-gamelogs.html"

    # TODO: Maybe try/catch here for timeout?
    sleep(10)  # Don't spam the server
    res = requests.get(url)
    if res is None or not res.ok:  # If we don't get a good response
        print(
            f"----WARNING ({res.status_code}): {fmt_team} got no/bad response from SportsReference.com"
        )
        return

    soup = bs4.BeautifulSoup(res.text, features="html.parser")
    table = soup.select_one("tbody")
    if table is None:
        print(f"----WARNING: {fmt_team} {gender} {year} doesn't have a table body.")
        return

    # Make the year folder
    os.makedirs(os.path.dirname(outfile), exist_ok=True)

    # Get the table headers and other content and write it to a .csv file
    # headers = [str(th.text) for th in table.select("tr th")]
    with open(outfile, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerows(
            [[str(td.text) for td in row.find_all("td")] for row in table.select("tr")]
        )


def get_team_files(year: int, gender: str, teams_file: str = "./teams/teams.txt"):
    """
    Requests gamelogs for every team listed in a given team file for a given year.
    Writes the gamelog table to a file in the games folder corresponding to the team's name.
    """

    with open(teams_file, "r") as teams:
        for team in teams:
            fmt_team = "-".join(team[:-1].split(" "))  # format team name to match url
            print(f"Scraping {fmt_team} {gender} {year}")
            get_team_file(fmt_team, year, gender)
