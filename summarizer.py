"""
This script summarizes every game played by every team in the 2018-2019 season
into a lists, where each list entry is a list containing the opponent, whether
the team won (True) or lost (False), the home team score, and the away team 
score.
This list of lists is then serialized into a "summary" file called 
[TEAM_NAME]_summary.p.
"""

import csv
import pickle

teamFile = "./teams/teams.txt"
team_list = []

def summarize_team_file(dashed_team_name):
    with open("./games/"+dashed_team_name+"_games.csv", 'r', newline='') as in_csv:
        reader = csv.reader(in_csv)

        new_rows = []
        for row in reader:
            if len(row)==0 or len(row[0])==0: continue
            
            # Trying my best to format opponents the same way they are in the teams file.
            # The team file matches the url on SportsReference. r/programminghorror
            opponent = row[2].lower().replace('.','').replace('&','').replace('-',' ').replace('(','').replace(')','').replace('\'','')
            if opponent == "unc": opponent = "north carolina"
            elif opponent == "unc asheville": opponent = "north carolina asheville"
            elif opponent == "unc wilmington": opponent = "north carolina wilmington"
            elif opponent == "nc state": opponent = "north carolina state"
            elif opponent == "uc davis": opponent = "california davis"
            elif opponent == "uc riverside": opponent = "california riverside"
            elif opponent == "uc santa barbara": opponent = "california santa barbara"
            elif opponent == "uc irvine": opponent = "california irvine"
            elif opponent == "purdue fort wayne": opponent = "ipfw"
            elif opponent == "texas rio grande valley": opponent = "texas pan american"
            elif opponent == "omaha": opponent = "nebraska omaha"
            elif opponent == "little rock": opponent = "arkansas little rock"
            elif opponent == "louisiana": opponent = "louisiana lafayette"
            elif opponent == "lsu": opponent = "louisiana state"
            elif opponent == "usc": opponent = "southern california"
            elif opponent == "usc upstate": opponent = "south carolina upstate"
            elif opponent == "ole miss": opponent = "mississippi"
            elif opponent == "unlv": opponent = "nevada las vegas"
            elif opponent == "siu edwardsville": opponent = "southern illinois edwardsville"
            elif opponent == "ut martin": opponent = "tennessee martin"
            elif opponent == "ucf": opponent = "central florida"
            elif opponent == "uconn": opponent = "connecticut"
            elif opponent == "smu": opponent = "southern methodist"
            elif opponent == "umass": opponent = "massachusetts"
            elif opponent == "umass lowell": opponent = "massachusetts lowell"
            elif opponent == "penn": opponent = "pennsylvania"
            elif opponent == "vcu": opponent = "virginia commonwealth"
            elif opponent == "umkc": opponent = "missouri kansas city"
            elif opponent == "byu": opponent = "brigham young"
            elif opponent == "uic": opponent = "illinois chicago"
            elif opponent == "pitt": opponent = "pittsburgh"
            elif opponent == "uncg": opponent = "north carolina greensboro"
            elif opponent == "etsu": opponent = "east tennessee state"
            elif opponent == "saint marys": opponent = "saint marys ca"
            elif opponent == "utep": opponent = "texas el paso"
            elif opponent == "ucsb": opponent = "california santa barbara"
            elif opponent == "greensboro": opponent = "north carolina greensboro"
            elif opponent == "central connecticut": opponent = "central connecticut state"
            elif opponent == "umbc": opponent = "maryland baltimore county"
            elif opponent == "st peters": opponent = "saint peters"
            elif opponent == "st josephs": opponent = "saint josephs"
            elif opponent == "st josephs ny": opponent = "saint josephs"
            elif opponent == "central connecticut": opponent = "central connecticut state"
            elif opponent == "utsa": opponent = "texas san antonio"
            elif opponent == "unc greensboro": opponent = "north carolina greensboro"
            elif opponent == "massachusetts boston": opponent = "massachusetts"
            elif opponent == "tcu": opponent = "texas christian"
            elif opponent == "southern miss": opponent = "southern mississippi"
            elif opponent == "vmi": opponent = "virginia military institute"
            elif opponent == "william  mary": opponent = "william mary"
            elif opponent == "missouri st": opponent = "missouri state"
            elif opponent == "detroit": opponent = "detroit mercy"
            
            win = "W" in row[3]
            home_score, away_score = int(row[4]), int(row[5])
            
            new_rows.append([opponent, win, home_score, away_score])

    return new_rows
                
with open(teamFile, 'r') as teams:
    for team in teams:
        fmt_team = '-'.join(team[:-1].split(' '))
        #print(fmt_team)
        
        summary = summarize_team_file(fmt_team)
        if summary is None or len(summary) == 0: raise Exception()
        
        pickle.dump(summary, open("./summaries/"+fmt_team+"_summary.p",'wb'))
        
#print(team_list)