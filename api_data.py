import json
import requests
import config as cfg


def get_info_from_api(team_name):
    if "-" in team_name:
        team_name = team_name.replace("-", "+")
    if "brighton" in team_name:
        team_name = "brighton"
    if "leicester" in team_name:
        team_name = "leicester"
    if "norwich" in team_name:
        team_name = "norwich"
    if "mallorca" in team_name:
        team_name = "mallorca"
    if "parma" in team_name:
        team_name = "parma+calcio"
    if "bayern" in team_name:
        team_name = "bayern"
    if "koln" in team_name:
        team_name = "fc+koln"
    if "union+berlin" in team_name:
        team_name = "union+berlin"
    if "fsv+mainz" in team_name:
        team_name = "mainz"
    if "hoffenheim" in team_name:
        team_name = "hoffenheim"
    if "mgladbach" in team_name:
        team_name = "borussia+monchengladbach"
    if "schalke" in team_name:
        team_name = "schalke"
    if "leverkusen" in team_name:
        team_name = "leverkusen"
    if "paderborn" in team_name:
        team_name = "paderborn"
    print(team_name)
    response = requests.get(cfg.API_URL + team_name)
    team_data = json.loads(response.text)
    return team_data['teams'][0]

