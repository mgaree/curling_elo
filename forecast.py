#!/usr/bin/python3

"""
This file:
- reads input csv of teams and their initial Elo ratings (e.g. at start of season/tournament)
--- filename defaults to ./data/initial_elos.csv
- reads input csv of games history with results and scheduled games
--- filename passed to Forecast.forecast()
- forecasts win probabilities for all games
- adjusts team Elo ratings based on results for completed games
- saves schedule to file with Elo ratings and win probabilities
--- filename is games_filename + ".forecasted.csv"

Borrows heavily from https://github.com/fivethirtyeight/nfl-elo-game/blob/master/forecast.py

Notes:
- If a team has multiple scheduled-but-incomplete games, the team will have the same pre-game Elo
rating for those games.
- all field headers should be present in input file even if the data is blank

"""


import math

from util import Util

K = 20.0  # The speed at which Elo ratings change; same value as 538's NFL Elo
REVERT = 1/3.0  # Between seasons, a team retains 2/3 of its previous season's rating
MEAN_ELO = 1600.0  # Average/initial Elo rating used for between-season reversion; 538 NFL uses 1505


class Forecast:

    @staticmethod
    def forecast(games_filename):
        """ Generates win probabilities in the elo_prob1 field for each game based on Elo model """

        # Initialize team objects to maintain ratings
        teams = Util.read_initial_elos()

        # Load games history
        games = Util.read_games(games_filename)

        # For each game, compute Elo-based win probability & update Elo ratings for completed games
        for game in games:
            team1, team2 = teams[game['team1']], teams[game['team2']]

            # Revert teams at the start of seasons
            for team in [team1, team2]:
                # don't revert on first season and revert when this game is in a new season for team
                if (team['season'] is not None) and (game['season'] != team['season']):
                    team['elo'] = MEAN_ELO*REVERT + team['elo']*(1-REVERT)
                team['season'] = game['season']

            # Update games entry with pre-game, post-reversion Elo ratings for later file writing
            game['elo1'] = team1['elo']
            game['elo2'] = team2['elo']

            # Difference in team Elo ratings alone used in Elo probability calculation
            elo_diff = team1['elo'] - team2['elo']

            # This is the most important piece, where we forecast the win probability for team1
            game['elo_prob1'] = 1.0 / (math.pow(10.0, (-elo_diff/400.0)) + 1.0)

            # If game was played, adjust team Elo ratings
            if game['result1'] is not None:
                # This system ignores game points; FiveThirtyEight does not
                # Previously had a note about autocorrelation, but it only applies for game points

                # Elo shift based on K
                shift = K * (game['result1'] - game['elo_prob1'])

                # Apply shift to get post-game Elo rating; will be pre-game rating for team's next game
                # Note: final Elo ratings will not be saved to a file; could add as future mod
                team1['elo'] += shift
                team2['elo'] -= shift

        Util.write_games(games, games_filename + ".forecasted.csv")
