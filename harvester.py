"""This script will run a scraper program to get gamelog data from 
SportsReference.com for all teams listed in a file containing the formatted
names of Division I NCAA Basketball teams for a given year.

This information will then be saved to a .csv file in subfolder of the
games folder corresponding to the specific year queried.

These .csv files will then themselves be scraped by a cleaner program that will
extract the relevant information (opponent and score) and serialize it.

The cleaner will then combine this information into a large serialized file
for all schools to be used by the ranker program.

NOTE
The format of the teams file should be a .txt file with one team per line.
These team names should match those in the URLs on SportsReference.com;
however, dashes between words in school names are optional.
Some examples of things SportsReference does their URLs:
    *   All names are in lower case.
    *   Schools called "University of [state]" are just called [state].
            University of North Carolina --> north carolina
            Univeristy of California --> california
    *   Acronyms and other abbreviations teams are (usually) extended.
        The most notable exception are schools with long names.
            NC State --> north carolina state
            UC Davis --> california davis
            Indiana University Purdue University Fort Wayne --> ipfw
            New Jersey Institute of Technology --> njit
    *   The characters &, ', ., (, and ) are removed.
            William & Mary --> william mary
            St. Johns (NY) --> st johns ny
    *   The offical names from schools are prefered to common nicknames.
            Old Miss --> mississippi
            Mizzou --> missouri
"""

import scraper
import cleaner

def harvest(year, teams_file="./teams/teams.txt"):
    """Scrapes, cleans, and serializes data given a list of properly-formatted
    teams in a given file for a given year.

    If a team on the list cannot be found for a given year (likely it's not D1)
        North Alabama, pre-2019
        Savannah State, post-2019
    the program will print an message containing "WARNING" several times throughout
    the execution.
    The program will not print any error message if a team is "missing

    For all 350+ D1 teams, this process takes about 2.5 minutes, with more than 95%
    of that time coming from the web-scraping part. If this function seems to be
    taking much longer on the scraping part, hitting Crtl+C on the keyboard, which
    will kill a thread of execution hanging on web input, should resume the program.
    After hitting Ctrl+C, you'll likely see a "WARNING" message appear.
    """
    print("Scraping gamelogs")
    scraper.get_team_files(year, teams_file)
    
    print("Summarizing gamelogs")
    cleaner.summarize_team_files(year, teams_file)
    
    print("Combining gamelogs")
    cleaner.combine_summaries(year, teams_file)