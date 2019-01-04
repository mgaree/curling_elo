#!/usr/bin/python3

"""

Utility methods for curling_elo package.

"""


import csv


class Util:

    @staticmethod
    def read_games(filename):
        """ Load games history from file. """
        games = [item for item in csv.DictReader(open(filename))]

        # apply typecasting to data
        for game in games:
            game['elo_prob1'] = float(game['elo_prob1']) if game['elo_prob1'] != '' else None
            game['result1'] = float(game['result1']) if game['result1'] != '' else None

        return games

    @staticmethod
    def write_games(games, filename):
        """ Write games data to file """
        fieldnames = 'date,season,playoff,team1,team2,result1,elo1,elo2,elo_prob1'.split(',')

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(map(Util.format_game_entry, games))

        print("Games data saved to " + filename)

    @staticmethod
    def read_initial_elos(filename="data/initial_elos.csv"):
        """ Read initial Elo ratings for teams """
        teams = {}
        for row in [item for item in csv.DictReader(open(filename))]:
            teams[row['team']] = {
                'name': row['team'],
                'season': None,  # tracker to handle between-season rating reversion
                'elo': float(row['elo'])
            }

        return teams

    @staticmethod
    def format_game_entry(game):
        """ Apply text formatting to game entry before writing to file """
        g = game.copy()  # pylint: disable=invalid-name

        if g['result1'] is not None and g['result1'] != 0.5:
            g['result1'] = int(g['result1'])

        for field in ['elo1', 'elo2', 'elo_prob1']:
            g[field] = "%.5f" % g[field]

        return g
