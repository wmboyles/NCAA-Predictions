"""
This script gets a history of all games played by all division I NCAA 
basketball teams in the 2018-2019 season.
For each team listed in the file ./teams/teams.txt, this script makes
a request to SportsReference.com for 2019 gamelogs. This information is then
parsed and written to a csv file called ./games/[TEAM_NAME]_games.csv.
This csv file is in the correct format to be read by cleaner.py.
"""

import requests
import bs4
import csv

#<table .*>.*</table>
url_fmt = "https://www.sports-reference.com/cbb/schools/{0}/{1}-gamelogs.html"
year = 2019

with open("./teams/teams.txt", 'r') as teams:
    for team in teams:
        fmt_team = '-'.join(team[:-1].split(' '))
        url = url_fmt.format(fmt_team, year)
        print(fmt_team)
        
        res = requests.get(url)
        if res is None:
            print("----ERROR:",fmt_team,"got no response from SportsReference.com")
            continue

        soup = bs4.BeautifulSoup(res.text)
        table = soup.select_one("table")
        if table is None or len(table) == 0:
            print("----ERROR:",fmt_team,"doesn't have a table. This probably means the URL was bad.")
            continue
        
        headers = [str(th.text) for th in table.select("tr th")]
        
        with open("./games/"+fmt_team+"_games.csv", 'w', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(headers)
            wr.writerows([[str(td.text) for td in row.find_all("td")] for row in table.select("tr + tr")])