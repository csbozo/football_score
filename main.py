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
    args = parser.parse_args()

    if args.SerieA:
        leagues.append("seriea")
    if args.PremierLeague:
        leagues.append("premier")
    if args.LaLiga:
        leagues.append("laliga")
    if args.BundesLiga:
        leagues.append("bundes")

    return leagues


# A função main() precisa ser assíncrona porque ela irá 'await' outras funções assíncronas
async def main():
    """
    this is main calling function to extract players data out of https://www.sofascore.com
    """

    leagues_to_download = parsing()  # getting commands from the cli
    print(leagues_to_download)

    for league in leagues_to_download:  # iterating league links
        league_name = cfg.TOP_LEAGUES_URLS[league].split("/")[-2]

        teams = await hp.extract_teams_urls(cfg.TOP_LEAGUES_URLS[league])  # extracting teams out of leagues tables

        print("\ngetting teams from " + league_name)  # printing for user "loading" in addition to tqdm
        watch = tqdm(total=len(teams), position=0)
        for team_url in teams:  # iterating all teams urls
            team_name = team_url.split('/')[-2]
            print(team_name)
            manager_url = await hp.extract_mgr_url(team_url)  # Assumindo que extract_mgr_url é async
            manager_info = hp.extract_mgr_info(manager_url)  # extract_mgr_info não é async, então não precisa de await

            players_list = await hp.extract_players_urls(team_url)  # extracting player url which

            print(manager_info)
            print(players_list)
            watch.update(1)


if __name__ == '__main__':
    asyncio.run(main())
