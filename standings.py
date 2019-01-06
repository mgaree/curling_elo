#!/usr/bin/python3

"""
This file:
- takes games history and outcomes for a tournament
- computes current standings for tournament using tiebreaker rules
--- uses all completed games in csv file, not just last completed round

* this file does not care about Elo scores. "ranking" here refers to position in the standings.

TODO: write better documentation

"""

import random  # U(0, 1) used as final tiebreaker level
import pandas as pd  # working with a pd.DataFrame allows for easy row-sums and submatrices


class Standings:

    tiebreaker_labels = {1: 'by points', 2: 'by head-to-head points',
                         3: 'by vs-1st-place', 4: 'by vs-2nd-place', 5: 'by random'}

    @staticmethod
    def get_contenders(df):  # pylint: disable=invalid-name
        """ Return team names for those tied for most wins """
        total_wins = df.sum(axis=1)
        max_wins = total_wins.max()  # get row sums for df
        contenders = total_wins.where(lambda x: x == max_wins).dropna()
        return list(contenders.index.values)

    @staticmethod
    def compute_standings(teams, games):
        """ Return standings dict for completed games in round robin tournament

        The approach here is to assign teams to rankings from 1st place to Nth, rather than
        break ties first. Later tie breakers depend on 1st & 2nd place, so this is useful.

        """
        unassigned_teams = list(teams.keys())  # shrinks as a team is assigned to a ranking

        standings = {}  # standings[i] = (name of i-th place team, tiebreaker used)
        contenders = []  # list of teams in contention (tied) for selection at each ranking

        # build master matrix of wins for each team vs each other team
        wins_df = Standings.get_wins_df(teams, games)  # win counts for each pair of teams

        for i in range(1, len(teams)+1):  # range is [start, stop), so +1
            tiebreak_level = 1

            # apply tiebreakers until a team is selected for i-th place ranking;
            # the final tiebreak level will always select one team, so this loop is not infinite
            while True:
                contenders = Standings.get_contenders_for_tiebreak_level(
                    tiebreak_level, contenders, wins_df, unassigned_teams, standings)

                if len(contenders) == 1:
                    # tie is broken for the current rank, so stop applying tiebreakers
                    break
                else:
                    # a tie remains, so move to next level of tiebreakers
                    tiebreak_level += 1

            # tiebreakers have been applied and only one team is contending for i-th place ranking
            standings[i] = (contenders[0], Standings.tiebreaker_labels[tiebreak_level])

            # since this team has been assigned to standings, remove it from future consideration
            unassigned_teams.remove(contenders[0])

        # endfor

        # error checking
        assert not unassigned_teams  # all teams assigned to standings
        assert not [k for (k, v) in standings.items() if v is None]  # all ranks assigned a team

        return standings  # want saving to file to be decoupled from generating standings.

    @staticmethod
    def get_contenders_for_tiebreak_level(tiebreak_level, past_contenders, wins_df, unassigned_teams, standings):
        """ Return list of teams contending for current ranking based on tiebreaker level

        past_contenders is list of contenders selected at previous tiebreaking level; it is ignored
        for the first level, which cares about all unassigned teams.

        """

        # First level: overall wins
        if tiebreak_level == 1:
            # select teams with highest overall wins among unassigned teams
            contenders = Standings.get_contenders(wins_df.loc[unassigned_teams])

        # Second level: head-to-head wins among tied group (past contenders)
        elif tiebreak_level == 2:
            # select teams with highest overall wins as though tournament had been played only
            # with past contenders (i.e. head-to-head results)
            contenders = Standings.get_contenders(wins_df.loc[past_contenders, past_contenders])

        # Third level: wins vs. 1st-place team (if 1st-place has been chosen)
        elif tiebreak_level == 3:
            if 1 not in standings:
                # standings are assigned in order, 1 to N. if 1st-place has not been assigned,
                # then we're breaking a tie for 1st-place and this level is n/a.
                # we could jump directly to random selection, since 2nd-place is also not assigned,
                # but instead we'll 'do nothing' so the calling function can properly track the
                # tie breaking level; it's a little inefficient, but only happens once
                contenders = past_contenders
            else:
                # using to_frame to cast Series as DataFrame for compatibility with get_contenders
                contenders = Standings.get_contenders(wins_df.loc[past_contenders, standings[1][0]].to_frame())

        # Fourth level: wins vs. 2nd-place team (if 2nd-place has been chosen)
        elif tiebreak_level == 4:
            if 2 not in standings:
                # same logic as for previous level and 1st-place
                contenders = past_contenders
            else:
                contenders = Standings.get_contenders(wins_df.loc[past_contenders, standings[2][0]].to_frame())

        # Final level: random selection
        else:
            contenders = [random.choice(past_contenders)]

        return contenders

    @staticmethod
    def get_wins_df(teams, games):
        """ Return NxN data frame of team Row's # of wins against team Column.

        e.g.
             RII  STP  BFF
        RII    0    1    0
        STP    0    0    1
        BFF    1    0    0

        means that RII beat STP 1x, STP beat BFF 1x, and BFF beat RII 1x.

        So, the row sum is the teams total wins, and the column sum is the teams total losses.

        This approach makes it easy to get total wins as well as head-to-head wins using submatrices.

        """
        names = teams.keys()
        df = pd.DataFrame(index=names, columns=names, data=0)  # pylint: disable=invalid-name

        for game in games:
            if game['result1'] == 1:
                df.loc[game['team1'], game['team2']] += 1
            elif game['result1'] == 0:
                df.loc[game['team2'], game['team1']] += 1
            else:
                pass  # draws not supported

        return df


#### main for testing
#from util import Util
#teams = Util.read_initial_elos('data/teams3.csv')
#games = Util.read_games('data/games3.csv')
#
#standings = Standings.compute_standings(teams, games)
#print(standings)
