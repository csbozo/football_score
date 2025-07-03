# README -  SofaScore Scraper

## Overview

This Data Engineering project performs some detailed Data Mining operations, reaching the website [SofaScore](https://www.sofascore.com/) and scraping data about football players and managers from the main european leagues.

## The Data

For the selected football leagues, all the team names are collected.

For every team, each player is scraped, and a series of information is stored:

```
1. Name
2. Nationality
3. Date of Birth
4. Height
5. Preferred Foot
6. Position on the Pitch
7. Shirt Number
```

Information about managers is parsed as well:

```
1. Name
2. Date of Birth
3. Nationality
4. Preferred Formation
5. Average Points per Game
6. Games Won
7. Games Drawn
8. Games Lost
```

## Usage

As a first step it's important to write the correct username and password in "config.py".
Then, just run the following commands:

```
pip install -r requirements.txt
```

```
python main.py -s -p -l -b
```

CLI Arg | Action
------------ | ------------- 
-s | scrapes teams and players from Serie A
-p | scrapes teams and players from Premier League
-l | scrapes teams and players from La Liga
-b | scrapes teams and players from Bundesliga
-cwc | scrapes teams and player from FIFA Club World Cup

The user can choose which league or combination of leagues to scrape and to create/update the database with.

## Created by:
- Rodrigo Pires
