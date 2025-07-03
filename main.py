import config as cfg
import html_parser as hp  # Assumindo que este módulo contém as funções Playwright
from tqdm import tqdm
import argparse
import asyncio  # Importar asyncio para lidar com funções assíncronas
import json


def parsing():
    """
    using argparse to simplify the cli for the user
    """
    leagues = []
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--SerieA", help="download Italian league players", action="store_true")
    parser.add_argument("-p", "--PremierLeague", help="download English league players", action="store_true")
    parser.add_argument("-l", "--LaLiga", help="download Spanish league players", action="store_true")
    parser.add_argument("-b", "--BundesLiga", help="download German league players", action="store_true")
    parser.add_argument("-cwc", "--FifaClubWorldCup", help="download Fifa Club World Cup players", action="store_true")
    args = parser.parse_args()

    if args.SerieA:
        leagues.append("seriea")
    if args.PremierLeague:
        leagues.append("premier")
    if args.LaLiga:
        leagues.append("laliga")
    if args.BundesLiga:
        leagues.append("bundes")
    if args.FifaClubWorldCup:
        leagues.append("clubcup")

    return leagues


# A função main() precisa ser assíncrona porque ela irá 'await' outras funções assíncronas
async def main():
    """
    essa main chama as funções para extrair os dados dos jogadores da origem https://www.sofascore.com
    """

    leagues_to_download = parsing()  # recebendo o comando CLI para capturar as ligas
    print(leagues_to_download)
    all_team_names = []
    all_manager_info = []
    all_player_lists = []

    for league in leagues_to_download:  # capturando a url das ligas
        league_name = cfg.TOP_LEAGUES_URLS[league].split("/")[-2]

        teams = await hp.extract_teams_urls(cfg.TOP_LEAGUES_URLS[league])  # extraindo as urls das ligas

        print("\ngetting teams from " + league_name)  # exibindo o nome da liga a ser capturada
        watch = tqdm(total=len(teams), position=0)
        for team_url in teams:  # iterando todas as urls de time
            team_name = team_url.split('/')[-2]
            manager_url = await hp.extract_mgr_url(team_url)
            manager_info = hp.extract_mgr_info(manager_url)  # extract_mgr_info não é async, então não precisa de await

            players_list = await hp.extract_players_urls(team_url)  # extraindo url dos jogadores

            all_team_names.append(team_name)
            all_manager_info.append(manager_info)
            all_player_lists.append(players_list)

            print(team_name)
            print(manager_info)
            print(players_list)
            watch.update(1)
        watch.close()
    with open("team_name.txt", mode='w', encoding='utf-8') as arquivo:
        arquivo.write("\n".join(all_team_names))

    with open("list_manager_info.txt", mode='w', encoding='utf-8') as arquivo:
        arquivo.write("\n".join(str(item) for item in all_manager_info))

    with open("list_player_list.txt", mode='w', encoding='utf-8') as arquivo:
        json_lines = []
        for player_dict in all_player_lists:
            json_lines.append(json.dumps(player_dict))  # Converte o dicionário para uma string JSON
        arquivo.write("\n".join(json_lines))


if __name__ == '__main__':
    asyncio.run(main())
