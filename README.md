This repository contains code and data for creating Elo ratings and forecasts for curling league as well as creating league standings.

* Borrows heavily from https://github.com/fivethirtyeight/nfl-elo-game

## Example

Try `Forecast.forecast('data/games.csv')`

## Input file notes

initial_elos.csv fields: `team,elo`

* `team` unique identifier for team
* `elo` initial Elo score at beginning of time / before playing first game in games history

This file allows seasons to be independent of each other, and/or teams to start with other than the
default rating. e.g. the previous season used a different K value than the current one

games.csv fields: `date,season,playoff,team1,team2,result1,elo1,elo2,elo_prob1`

* `date` and `playoff` fields currently unused
* `season` triggers between-season ratings reversion; can be any data type
* `elo1` and `elo2` are team1 and team2's pre-game Elo ratings; `forecast()` will replace them
* `elo_prob1` is probability of team1 winning based on elo1 and elo2; `forecast()` will replace this
* `result1` = 1 if team1 wins, 0 if team1 loses, 0.5 if the game is a draw

Entries are assumed to be already sorted by season

## Other references
https://fivethirtyeight.com/methodology/how-our-nfl-predictions-work/
http://math.bu.edu/people/mg/ratings/approx/approx.html
https://www.fide.com/component/handbook/?id=197&view=article
