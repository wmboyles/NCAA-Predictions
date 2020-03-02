import numpy as np
import pickle
import os

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from enum import Enum

# Indexes of different items in total_summary entries
class GameValues(Enum):
    HOME_TEAM = 0  
    AWAY_TEAM = 1
    WIN_LOSS = 2
    HOME_SCORE = 3
    AWAY_SCORE = 4
    HOME_eFGp = 5
    AWAY_eFGp = 6
    HOME_TOVp = 7
    AWAY_TOVp = 8
    HOME_ORBp = 9
    AWAY_ORBp = 10
    HOME_FTR = 11
    AWAY_FTR = 12

class GameWeights(Enum):
    WEIGHTS = [7.0, 4.0, 2.5, 2.0, 1.75]


def rank(year, alpha=.85, iters=3500, print_rankings=True, plot_rankings=False, serialize_results=True):
    total_summary = pickle.load(open("./summaries/"+str(year)+"/total_summary.p", 'rb'))
    
    teams = list(set([game[GameValues.HOME_TEAM.value] for game in total_summary]))
    num_teams = len(teams)

    mat, vec = np.zeros((num_teams, num_teams)), np.ones((num_teams, 1))
    
    for game in total_summary:
        if game[GameValues.HOME_TEAM.value] in teams and game[GameValues.AWAY_TEAM.value] in teams and not game[GameValues.WIN_LOSS.value]:
            # Game winner -- 5
            home_pr_score, away_pr_score = 0.0, GameWeights.WEIGHTS.value[0] # Accounts for winner of game

            # eFG% -- 4
            if game[GameValues.HOME_eFGp.value] > game[GameValues.AWAY_eFGp.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[1]
            elif game[GameValues.AWAY_eFGp.value] > game[GameValues.HOME_eFGp.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[1]
            
            # TO% -- 2.5
            if game[GameValues.HOME_TOVp.value] > game[GameValues.AWAY_TOVp.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[2]
            elif game[GameValues.AWAY_TOVp.value] > game[GameValues.HOME_TOVp.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[2]

            # OR% -- 2
            if game[GameValues.HOME_ORBp.value] > game[GameValues.AWAY_ORBp.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[3]
            elif game[GameValues.AWAY_ORBp.value] > game[GameValues.HOME_ORBp.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[3]

            # FTR -- 1.5
            if game[GameValues.HOME_FTR.value] > game[GameValues.AWAY_FTR.value]: 
                home_pr_score += GameWeights.WEIGHTS.value[4]
            elif game[GameValues.AWAY_FTR.value] > game[GameValues.HOME_FTR.value]: 
                away_pr_score += GameWeights.WEIGHTS.value[4]


            home_idx = teams.index(game[GameValues.HOME_TEAM.value])
            away_idx = teams.index(game[GameValues.AWAY_TEAM.value])

            mat[home_idx, away_idx] += home_pr_score
            mat[away_idx, home_idx] += away_pr_score

    mat = (alpha*mat) + (1-alpha)*np.ones((num_teams, num_teams)) / num_teams

    for i in range(iters):
        vec = mat @ vec
        vec *= num_teams / sum(vec)

    sorted_pairs = sorted([(prob[0], team) for team,prob in zip(teams, vec)])
    if print_rankings:
        for i in range(len(sorted_pairs)): print(num_teams-i, sorted_pairs[i])

    if serialize_results:
        # Make the year folder
        outfile = "./predictions/"+str(year)+"/_rankings.p"
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        pickle.dump(sorted_pairs, open(outfile, 'wb'))

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

rank(2020, alpha=1, serialize_results=False)