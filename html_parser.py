import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from playwright.async_api import async_playwright
import asyncio
import config as cfg
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
    "Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
    # Adicione mais User-Agents reais aqui
]

arrow_manipu = lambda x: x.replace("<", ">").split(">")


async def get_browser_page():
    # Inicia o Playwright e lança o navegador Chromium
    # headless=True para não abrir uma janela visível do navegador

    # playwright = await async_playwright().start()
    # browser = await playwright.chromium.launch(headless=True)
    # page = await browser.new_page()
    # return browser, page

    playwright = await async_playwright().start()
    # Escolha um User-Agent aleatório
    selected_user_agent = random.choice(user_agents)
    browser = await playwright.chromium.launch(headless=True)
    # Passe o User-Agent ao criar o contexto da página
    page = await browser.new_page(user_agent=selected_user_agent)
    return browser, page


def extract_player_info(player_url):
    """
    A função extrai as informações mais interessantes de um jogador, se disponíveis, a partir da URL da página
    do jogador em https://www.sofascore.com, e as retorna em um dicionário.
    player_url: URL do jogador no site https://www.sofascore.com.
    Retorna: Dicionário com as seguintes chaves: Nome, Nacionalidade, Data de Nascimento,
    Altura, Pé Preferencial, Posição, Número da Camisa, Média de Avaliação no Site.
    """
    player_dict = {}
    player_html = BeautifulSoup(requests.get(player_url).text, 'html.parser')
    player_panel_html = player_html.find_all("h2", class_="styles__DetailBoxTitle-sc-1ss54tr-5 enIhhc")
    details = arrow_manipu(str(player_panel_html))
    player_fields_html = player_html.find_all("div", class_="styles__DetailBoxContent-sc-1ss54tr-6 iAORZR")
    fields_list = arrow_manipu(str(player_fields_html))
    player_dict['name'] = player_url.split("/")[-2].replace('-', ' ').title()
    if "Nationality" in fields_list:
        raw_nationality = player_html.find_all("span", class_="u-pL8")
        player_dict['nationality'] = arrow_manipu(str(raw_nationality))[-3]
    for field in fields_list:
        try:
            b_day = parse(field, fuzzy=False)
            player_dict['birth_date'] = b_day
        except ValueError:
            continue

    for i in range(len(details)):
        is_a_detail = (r"h2 class=" in details[i] or r"span style" in details[i]) and details[i + 1] != ''
        if is_a_detail:
            if 'cm' in details[i + 1]:
                player_dict['height'] = int(details[i + 1].split()[0])
            elif details[i + 1] in cfg.POSSIBLE_FOOT:
                player_dict['prefd_foot'] = details[i + 1]
            elif details[i + 1] in cfg.POSSIBLE_POSITION:
                player_dict['position'] = details[i + 1]
            elif "Shirt number" in fields_list:
                player_dict['shirt_num'] = int(details[i + 1])

    for key in cfg.PLAYER_FIELDS:
        if key not in player_dict.keys():
            player_dict[key] = None
    return player_dict


async def extract_players_urls(team_url):
    players_list = []
    browser, page = await get_browser_page()
    try:
        await page.goto(team_url)
        # Opcional: esperar por um elemento específico para garantir que o JS carregou
        # await page.wait_for_selector("a.styles__CardWrapper-sc-1dlv1k5-15")

        team_html = BeautifulSoup(await page.content(), 'html.parser')

        all_players_html = team_html.find_all("div", class_="xYoiw")
        html_list = str(all_players_html).split()
        for line in html_list:
            if 'href="/football/player' in line:
                players_list.append(extract_player_info("https://www.sofascore.com" + line.split("\"")[1]))
    finally:
        await browser.close()
    return players_list


async def extract_mgr_url(team_url):
    mgr_link = ""
    browser, page = await get_browser_page()
    try:
        await page.goto(team_url)
        # Opcional: esperar por um elemento específico
        # await page.wait_for_selector('div.Content-sc-1o55eay-0.styles__ManagerContent-qlwzq-9.dxQrED')

        soup = BeautifulSoup(await page.content(), 'html.parser')

        mgr_html = soup.find_all('div', class_="fPSBzf bYPztT dJhvhl")
        if mgr_html:
            for line in str(mgr_html).split():
                if 'href' in line:
                    mgr_link = "https://www.sofascore.com" + line.split("\"")[1]
    finally:
        await browser.close()
    return mgr_link


def extract_mgr_info(manager_url):
    # Esta função não é assíncrona, portanto não usa await em requests.get
    # E 'manager_url' é esperado como a URL direta do gerente, não uma coroutine.
    try:
        mgr_dict = {}
        mgr_soup = BeautifulSoup(requests.get(manager_url).text, 'html.parser')
        mgr_dict['name'] = mgr_soup.find('h2', class_="hiWfit fdnFeu AxjtB").get_text()
        mgr_dict['nationality'] = mgr_soup.find('div', class_="fPSBzf bYPztT bYPznK fIXqzZ").get_text()
        values_list = arrow_manipu(str(mgr_soup.find_all('div', class_="fPSBzf iRgpoQ eluWnz dVzwSc eTCxQp")))
        mgr_dict['nationality'] = values_list[46]
        mgr_dict['birth_date'] = values_list[58]
        mgr_dict['pref. formation'] = values_list[74]
        mgr_dict['matches'] = values_list[86]
        mgr_dict['avg_points_per_game'] = values_list[98]
        values_list_2 = arrow_manipu(str(mgr_soup.find_all('div', class_="fPSBzf iRgpoQ fIXqzZ fzBPom")))
        mgr_dict['games_won'] = values_list_2[6]
        mgr_dict['games_drawn'] = values_list_2[10]
        mgr_dict['games_lost'] = values_list_2[14]
    except Exception:
        return None

    return mgr_dict


async def extract_teams_urls(league_url):
    team_list = []
    browser, page = await get_browser_page()
    try:
        await page.goto(league_url)
        team_html = BeautifulSoup(await page.content(), 'html.parser')
        all_teams_html = team_html.find_all("div", class_="fPSBzf bYPztT xYowp gnlqYH hYZFkb")
        html_list = str(all_teams_html).split()
        for line in html_list:
            is_line_with_link = "href=\"/team" in line and not line.endswith("img")
            # is_line_with_link = "href=" in line and not line.endswith("img")
            if is_line_with_link:
                team_list.append("https://www.sofascore.com" + line.replace("\"", "").split("=")[-1].split(">")[0])
    finally:
        await browser.close()
    sorted_teams = sorted(list(set(team_list)))
    return sorted_teams


async def extract_teams_urls_new(league_url):
    sorted_teams = ""
    browser, page = await get_browser_page()
    try:
        await page.goto(league_url)
        # Opcional: esperar por um elemento específico
        # await page.wait_for_selector('div.Content-sc-1o55eay-0.styles__ManagerContent-qlwzq-9.dxQrED')
        soup = BeautifulSoup(await page.content(), 'html.parser')
        mgr_html = soup.find_all('div', class_="TabPanel bpHovE")
        if mgr_html:
            for line in str(mgr_html).split():
                if '/time/' in line:
                    sorted_teams = "https://www.sofascore.com" + line.split("\"")[1]
                    print(line)
    finally:
        await browser.close()
    return sorted_teams


async def main():
    print("Iniciando a extração de URLs de times...")
    league_url_example = 'https://www.sofascore.com/pt/torneio/futebol/england/premier-league/17'
    teams = await extract_teams_urls_new(league_url_example)
    print(f"Número de times encontrados: {len(teams)}")
    print("Primeiros 5 times:", teams[:5])

    print("\nIniciando a extração de URLs de jogadores...")
    team_url_example = 'https://www.sofascore.com/team/football/arsenal/42'
    players = await extract_players_urls(team_url_example)
    print(f"Número de jogadores encontrados: {len(players)}")
    print("Primeiros 2 jogadores:", players[:2])

    print("\nIniciando a extração de URL e informações do gerente...")
    mgr_url = await extract_mgr_url(team_url_example)
    if mgr_url:
        print(f"URL do gerente: {mgr_url}")
        print("Informações do gerente:")
        mgr_info = extract_mgr_info(mgr_url)
        print(mgr_info)
    else:
        print("URL do gerente não encontrada.")


if __name__ == '__main__':
    # Isso inicia o loop de eventos assíncronos e executa a função main().
    asyncio.run(main())
