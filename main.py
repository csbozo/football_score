import config as cfg
import html_parser as hp  # Assumindo que este módulo contém as funções Playwright
import api_data as api
from tqdm import tqdm
import argparse
import asyncio  # Importar asyncio para lidar com funções assíncronas


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
    this is main calling function to extract players data out of https://www.sofascore.com
    """

    leagues_to_download = parsing()  # getting commands from the cli
    print(leagues_to_download)
    all_team_names = []
    all_manager_info = []
    all_player_lists = []

    for league in leagues_to_download:  # iterating league links
        league_name = cfg.TOP_LEAGUES_URLS[league].split("/")[-2]

        teams = await hp.extract_teams_urls(cfg.TOP_LEAGUES_URLS[league])  # extracting teams out of leagues tables

        print("\ngetting teams from " + league_name)  # printing for user "loading" in addition to tqdm
        watch = tqdm(total=len(teams), position=0)
        for team_url in teams:  # iterating all teams urls
            team_name = team_url.split('/')[-2]
            manager_url = await hp.extract_mgr_url(team_url)
            manager_info = hp.extract_mgr_info(manager_url)  # extract_mgr_info não é async, então não precisa de await

            players_list = await hp.extract_players_urls(team_url)  # extracting player url which

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
        all_player_urls = []
        for sublist in all_player_lists:
            all_player_urls.extend(sublist)  # Usa extend para adicionar todos os itens de uma sublista
        arquivo.write("\n".join(all_player_urls))


if __name__ == '__main__':
    asyncio.run(main())
