"""Gets a history of all games played by all division I NCAA 
basketball teams in the 2018-2019 season.
For each team listed in the file ./teams/teams.txt, this script makes
a request to SportsReference.com for 2019 gamelogs. This information is then
parsed and written to a csv file called ./games/[TEAM_NAME]_games.csv.
This csv file is in the correct format to be read by cleaner.py.
"""

import requests
import bs4
import csv
import os

url_fmt = "https://www.sports-reference.com/cbb/schools/{0}/{1}-gamelogs.html"


"""Request gamelogs from SportsReference.com given a dashed and formatted 
school name as described in get_team_files. Writes the information in the
gamelog table to a .csv file saved under the team's name.
"""
def get_team_file(fmt_team, year):
    url = url_fmt.format(fmt_team, year) # format the url to the specific team and year
            
    # TODO: Maybe try/catch here for timeout?
    res = requests.get(url)
    if res is None or not res.ok: # If we don't get a good response
        print("----WARNING:", fmt_team, "got no/bad response from SportsReference.com")
        return

    soup = bs4.BeautifulSoup(res.text, features="html.parser")
    table = soup.select_one("tbody") # Get the first table element on the page
    if table is None:
        print("----WANRING:", fmt_team, "doesn't have a table body.")
        return

    # Make the year folder
    outfile = "./games/"+str(year)+"/"+fmt_team+"_games.csv"
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    
    # Get the table headers and other content and write it to a .csv file
    #headers = [str(th.text) for th in table.select("tr th")]
    with open(outfile, 'w', newline='') as f:
        wr = csv.writer(f)
        #wr.writerow(headers)
        wr.writerows([[str(td.text) for td in row.find_all("td")] for row in table.select("tr")])

"""Requests gamelogs for every team listed in a given team file for a given
year and writes the gamelog table to a file in the games folder corresponding
to the team's name.
"""
def get_team_files(year, teams_file="./teams/teams.txt"):
    with open(teams_file, 'r') as teams:
        for team in teams:
            fmt_team = '-'.join(team[:-1].split(' ')) # format team name to match url
            print("Scraping",fmt_team,year)
            get_team_file(fmt_team, year)