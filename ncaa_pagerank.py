import numpy as np
import pickle
import os

import harvester

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from enum import Enum

class GameValues(Enum):
    """Items in this enum are the different indexes of the "four factor" statistics
    that the cleaner program extracts and claculates for each game.
    To use their value, you'd write game[GameValue.ITEM.value]

    In all instances, a high value of game[GameValue.ITEM.value] means a better team
    """
    HOME_TEAM = 0  # Name of first (called home but not always) team
    AWAY_TEAM = 1  # Name of second (called away but not always) team
    
    WIN_LOSS = 2  # Did the home/first team win?
    
    HOME_SCORE = 3  # The home/first team's score
    AWAY_SCORE = 4  # The away/second team's score
    
    HOME_eFGp = 5  # The home/first team's effective field goal percentage
    AWAY_eFGp = 6  # The away/second team's effective field goal percentage
    
    HOME_TOVp = 7  # The home/first team's turnover percentage
    AWAY_TOVp = 8  # The away/second team's turnover percentage
    
    HOME_ORBp = 9  # The home/first team's offensive rebound percentage
    AWAY_ORBp = 10  # The away/second team's offensive rebound percentage
    
    HOME_FTR = 11  # The home/first team's free throw rate
    AWAY_FTR = 12  # The away/second team's free throw rate

class GameWeights(Enum):
    """Items in this enum are the weights of a team winning  game and the
    "four factors". These weights can be changed to change the importance
    of these factors in each game.
    """
    WEIGHTS = [7.0, 4.0, 2.5, 2.0, 1.75]


def rank(year, alpha=.85, iters=3500, print_rankings=False, plot_rankings=False, serialize_results=True):
    """Ranks all Division I NCAA Basketball teams in a given year using PageRank.
    PARAMETERS
    year -->    The year that the NCAA championship game takes place.
                The 2019-2020 season would correpond to year=2020.
    alpha -->   A value between 0 and 1 that is a measure of randomness in
                PageRank meant to model the possibility that a user randomly
                navigates to a page without using a link. alpha=1 would be 
                completely deterministic, while alpha=0 would be completely
                random. Google is rumored to use alpha=.85, the default.
    iters -->   The number of iterations of PageRank matrix multiplication to
                perform. The deffault of iters=3500, about 10x the number of
                Division I teams, is generally sufficient for ranking.
    print_rankings -->  Should the function print out its rankings to stdout?
                        Defaults to False.
    plot_rankings -->   Should the function plot the rankings in sorted order?  
                        Defaults to False.
    serialize_results -->   Should the function save its rankings to a .p file
                            called "./predictions/[YEAR]/rankings.p"?
                            Defaults to True.
    """
    # Try to deserialize .p file summary. Try to create it if it doesn't exist
    try:
        total_summary = pickle.load(open("./summaries/"+str(year)+"/total_summary.p", 'rb'))
    except FileNotFoundError:
        print("----WARNING: No summary found for", year, "Trying to create summary...")
        try:
            harvester.harvest(year)
        except Error:
            print("---ERROR: Could not make summary for", year)
            return
        print("----SUCCESS: Summary created for", year)
        print("----Trying to rank again with newly created summary")
        rank(year, alpha, iters, print_rankings, plot_rankings, serialize_results)
        return
    
    # Get an ordered list of all the teams
    teams = list(set(['-'.join(game[GameValues.HOME_TEAM.value].split(' ')) for game in total_summary]))
    num_teams = len(teams)

    # Create PageRank matrix and initial vector
    mat, vec = np.zeros((num_teams, num_teams)), np.ones((num_teams, 1))
    for game in total_summary:
        # We only want to count games where both teams are D1 (in teams list)
        # We choose to only look at games where the first team won so we don't double-count games
        if game[GameValues.HOME_TEAM.value] in teams and game[GameValues.AWAY_TEAM.value] in teams and game[GameValues.WIN_LOSS.value]:
            # Game winner
            # Since we know the first/home team won, we can already assign the weight for that
            home_pr_score, away_pr_score = GameWeights.WEIGHTS.value[0], 0.0

            # Effective field goal percentage
            if game[GameValues.HOME_eFGp.value] > game[GameValues.AWAY_eFGp.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[1]
            elif game[GameValues.AWAY_eFGp.value] > game[GameValues.HOME_eFGp.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[1]
            
            # Turnover percentage
            if game[GameValues.HOME_TOVp.value] > game[GameValues.AWAY_TOVp.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[2]
            elif game[GameValues.AWAY_TOVp.value] > game[GameValues.HOME_TOVp.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[2]

            # Offensive rebound percentage
            if game[GameValues.HOME_ORBp.value] > game[GameValues.AWAY_ORBp.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[3]
            elif game[GameValues.AWAY_ORBp.value] > game[GameValues.HOME_ORBp.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[3]

            # Free throw rate
            if game[GameValues.HOME_FTR.value] > game[GameValues.AWAY_FTR.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[4]
            elif game[GameValues.AWAY_FTR.value] > game[GameValues.HOME_FTR.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[4]

            # Add weighted score for this game to matrix for both teams
            home_idx = teams.index(game[GameValues.HOME_TEAM.value])
            away_idx = teams.index(game[GameValues.AWAY_TEAM.value])

            mat[home_idx, away_idx] += home_pr_score
            mat[away_idx, home_idx] += away_pr_score

    # Alter the matrix to take into account our alpha factor
    mat = (alpha*mat) + (1-alpha)*np.ones((num_teams, num_teams)) / num_teams

    # Perform many iterations of matrix multiplication
    for i in range(iters):
        vec = mat @ vec
        vec *= num_teams / sum(vec) # Keep weights summed to set value (numerator)

    # Sort the (ranking, team) pair into a list of tuples
    sorted_pairs = sorted([(prob[0], team) for team,prob in zip(teams, vec)])

    # Print ranking pairs if specificed
    if print_rankings:
        for i in range(len(sorted_pairs)): print(num_teams-i, sorted_pairs[i])

    # Serialize results if specificed 
    # TODO: Serialize results as dict?
    if serialize_results:
        # Make the year folder
        outfile = "./predictions/"+str(year)+"/_rankings.p"
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        pickle.dump(sorted_pairs, open(outfile, 'wb'))

    # Plot graph of rankings if specified
    if plot_rankings:
        plt.plot(sorted(vec))
        plt.show()

def simulate_tourney(year):
    return
    # Deserialize ranking info for given year
    # Predict conference winners and add to tourney set with ranks
    # Add remaining 32-best teams to tourney with ranks
    # Seed teams based on ranks and randomly assign seeds to quadrants
    # Use seeding and quadrant info to arrange teams that will play each other next to each other
    # Simulate tournament in rounds, printing out predicted results and (confidence?)

yr = int(input("Year: "))
rank(year=yr, print_rankings=True, plot_rankings=True, serialize_results=True)