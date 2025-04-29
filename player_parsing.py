import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import warnings
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'util')))
from setup_selenium import setup_selenium
from pathlib import Path
from datetime_util import get_date_range
import re

# чтобы нормально работала структура проекта
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = f'{BASE_DIR}/data/processed/players_ranking.csv'
OUTPUT_FILE = f'{BASE_DIR}/data/processed/player_stats.csv'

# спарсить список матчей за период (23-24 год, с матчем сохранить название карты)
# парсить статы по этим картам
# парсить статы по ивентам

# начальная структура .csv
#   Player Name,Player ID,Link
# финальная структура .csv 
#   Player Name,Player ID,Player Link,Date,Team VS,Map,Result,Stats:{HLTV, DPR, KAST, IMPACT, ADR, KPR},Match Link
# добавлять результат и 

MAP_NAME_MAPPING = {
    "anc": "Ancient",
    "anb": "Anubis",
    "d2": "Dust2",
    "inf": "Inferno",
    "mrg": "Mirage",
    "nuke": "Nuke",
    "ovp": "Overpass",
    "vtg": "Vertigo",
    "trn": "Train",
}

def map_map_name(short_name): #ahah pun in the function name
    short_name = short_name.lower()
    if short_name not in MAP_NAME_MAPPING:
        warnings.warn(f"{short_name} отсутствует в маппинге названий карт")
        return short_name
    return MAP_NAME_MAPPING[short_name]

def parse_matches(player_link, driver, date_range):
    data = {
        "Date": [],
        "Team VS": [],
        "Result": [],
        "Map": [],
        "Match Link": []
    }
    # https://www.hltv.org/stats/players/matches/21167/donk?startDate=2023-01-01&endDate=2024-12-31
    # parse links to matches like
    # https://www.hltv.org/stats/matches/mapstatsid/189697/spirit-vs-faze?startDate=2023-01-01&endDate=2024-12-31&contextIds=21167&contextTypes=player
    # convert to
    # https://www.hltv.org/stats/matches/performance/mapstatsid/189697/spirit-vs-faze?startDate=2023-01-01&endDate=2024-12-31&contextIds=21167&contextTypes=player
    # sooo we need to find raphael-group-n-datalabel and parse from there ts belongs to raphael-group-n-parentgroup which belongs to raphael-paper-n which belongs to chartobject to unique chart to div class facts which belongs to standard box
    # so what we actually need is to go thru those players boxes, check headlines to match id, if id is matched then go and parse data from div class facts
    pattern = r"^https://www\.hltv\.org/player/(\d+)/([\w\-]+)$" #regex для извлечения айди и ника игрока
    match = re.match(pattern, player_link)
    url = f'https://www.hltv.org/stats/players/matches/{match.group(1)}/{match.group(2)}?{date_range}'
    print(url)
    driver.get(url)
    try:
        WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.stats-table tbody tr"))
    )  # Ожидание загрузки данных

        rows = driver.find_elements(By.CSS_SELECTOR, "table.stats-table tbody tr")
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) < 4:
                print('wtf')
                continue
            try:
                date = columns[0].text.strip()
                match_link_elements = row.find_elements(By.TAG_NAME, "a")
                match_link = match_link_elements[0].get_attribute('href')
                if match_link and "/stats/matches/mapstatsid/" in match_link:
                    match_link = match_link.replace(
                        "/stats/matches/mapstatsid/",
                        "/stats/matches/performance/mapstatsid/"
                    ) # мы же потом перейдем к сбору статы поэтому так
                score_1_match = re.search(r"\((\d+)\)", columns[1].text.strip())
                score_2_match = re.search(r"\((\d+)\)", columns[2].text.strip())
                score_1 = score_1_match.group(1)
                score_2 = score_2_match.group(1)
                score = f"{score_1} - {score_2}"
                team_2_links = columns[2].find_elements(By.TAG_NAME, "a")
                team_vs = team_2_links[0].text.strip()
                map_name = map_map_name(columns[3].text.strip())
                data["Date"].append(date)
                data["Team VS"].append(team_vs)
                data["Result"].append(score)
                data["Map"].append(map_name)
                data["Match Link"].append(match_link)
            except Exception as inner_e:
                print(f'{inner_e}')
    except Exception as e:
        print(f'Ошибка при парсинге списка матчей игрока {match.group(1)}: {e}')
    return pd.DataFrame(data)

def main():
    df_input_players = pd.read_csv(INPUT_FILE)
    TIME_RANGE = get_date_range(time_filter="2023-2024")
    driver = setup_selenium()
    
    all_matches = []
    for _, row in df_input_players.iterrows():
        try:
            player_name = row['Player Name']
            player_id = row['Player ID']
            player_link = row['Link']
            
            matches_df = parse_matches(player_link, driver, date_range=TIME_RANGE)
            
            matches_df["Player Name"] = player_name
            matches_df["Player ID"] = player_id
            matches_df["Player Link"] = player_link
            all_matches.append(matches_df)
        except Exception as e:
            print(f'Ошибка при добавлении данных в датафрейм: {e}')
        
    driver.quit()

    output_df = pd.concat(all_matches, ignore_index=True)
    column_order = ["Player Name", "Player ID", "Player Link", "Date", "Team VS", "Result", "Map", "Match Link"]
    output_df = output_df[column_order]
    output_df.to_csv(OUTPUT_FILE, index=False)
    
if __name__ == "__main__":
    main()