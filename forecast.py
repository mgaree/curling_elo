#!/usr/bin/python3

"""
This file:
- reads input csv of teams and their initial Elo ratings (e.g. at start of season/tournament)
--- filename hardcoded to data/initial_elos.csv
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


import csv
import math

K = 20.0  # The speed at which Elo ratings change; same value as 538's NFL Elo
REVERT = 1/3.0  # Between seasons, a team retains 2/3 of its previous season's rating
MEAN_ELO = 1600.0  # Average/initial Elo rating used for between-season reversion; 538 NFL uses 1505


class Forecast:

    @staticmethod
    def forecast(games_filename):
        """ Generates win probabilities in the elo_prob1 field for each game based on Elo model """

        # Initialize team objects to maintain ratings
        teams = {}
        for row in [item for item in csv.DictReader(open("data/initial_elos.csv"))]:
            teams[row['team']] = {
                'name': row['team'],
                'season': None,  # tracker to handle between-season rating reversion
                'elo': float(row['elo'])
            }

        # Load games history
        games = [item for item in csv.DictReader(open(games_filename))]
        for game in games:
            game['elo_prob1'] = float(game['elo_prob1']) if game['elo_prob1'] != '' else None
            game['result1'] = float(game['result1']) if game['result1'] != '' else None

        # For each game, compute Elo-based win probability & update Elo ratings for completed games
        for game in games:
            team1, team2 = teams[game['team1']], teams[game['team2']]

            # Revert teams at the start of seasons
            for team in [team1, team2]:
                # don't revert on first season and revert when this game is in a new season for team
                if (team['season'] is not None) and (game['season'] != team['season']):
                    team['elo'] = MEAN_ELO*REVERT + team['elo']*(1-REVERT)
                team['season'] = game['season']

            # Update games entry with pre-game Elo ratings for later file writing
            game['elo1'] = team1['elo']
            game['elo2'] = team2['elo']

            elo_diff = team1['elo'] - team2['elo']

            # This is the most important piece, where we forecast the win probability for team1
            game['elo_prob1'] = 1.0 / (math.pow(10.0, (-elo_diff/400.0)) + 1.0)

            # If game was played, maintain team Elo ratings
            if game['result1'] is not None:
                # This system ignores game points and autocorrelation; FiveThirtyEight does not

                # Elo shift based on K
                shift = K * (game['result1'] - game['elo_prob1'])

                # Apply shift to get post-game Elo rating; will be pre-game rating for team's next game
                team1['elo'] += shift
                team2['elo'] -= shift

        Forecast.save_forecast(games, games_filename)

    @staticmethod
    def save_forecast(games, games_filename):
        """ Write to file """
        save_filename = games_filename + ".forecasted.csv"
        fieldnames = 'date,season,playoff,team1,team2,result1,elo1,elo2,elo_prob1'.split(',')

        with open(save_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(map(Forecast.format_game_entry, games))

        print("Forecast saved to " + save_filename)

    @staticmethod
    def format_game_entry(game):
        """ Apply text formatting to game entry before writing to file """
        g = game.copy()

        if g['result1'] is not None and g['result1'] != 0.5:
            g['result1'] = int(g['result1'])

        for field in ['elo1', 'elo2', 'elo_prob1']:
            g[field] = "%.5f" % g[field]

        return g
