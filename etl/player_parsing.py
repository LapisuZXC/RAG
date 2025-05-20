import re
import warnings
from pathlib import Path

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.setup_selenium import setup_selenium
from util.datetime_util import get_date_from

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = f"{BASE_DIR}/data/processed/players_ranking.csv"
OUTPUT_FILE = f"{BASE_DIR}/data/processed/player_stats.csv"

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


def map_map_name(short_name: str) -> str:
    short_name = short_name.lower()
    if short_name not in MAP_NAME_MAPPING:
        warnings.warn(f"'{short_name}' отсутствует в маппинге названий карт")
        return short_name
    return MAP_NAME_MAPPING[short_name]


def parse_matches(player_link: str, driver, date_range: str) -> pd.DataFrame:
    data = {"Date": [], "Team VS": [], "Result": [], "Map": [], "Match Link": []}

    pattern = r"^https://www\.hltv\.org/player/(\d+)/([\w\-]+)$"
    match = re.match(pattern, player_link)

    if not match:
        warnings.warn(f"Некорректная ссылка на игрока: {player_link}")
        return pd.DataFrame(data)

    url = (
        f"https://www.hltv.org/stats/players/matches/{match.group(1)}/"
        f"{match.group(2)}?{date_range}"
    )
    print(f"Парсим: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table.stats-table tbody tr")
            )
        )

        rows = driver.find_elements(By.CSS_SELECTOR, "table.stats-table tbody tr")
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) < 4:
                continue
            try:
                date = columns[0].text.strip()
                match_link_element = row.find_element(By.TAG_NAME, "a")
                match_link = match_link_element.get_attribute("href")
                if "/stats/matches/mapstatsid/" in match_link:
                    match_link = match_link.replace(
                        "/stats/matches/mapstatsid/",
                        "/stats/matches/performance/mapstatsid/",
                    )

                score_1 = re.search(r"\((\d+)\)", columns[1].text.strip()).group(1)
                score_2 = re.search(r"\((\d+)\)", columns[2].text.strip()).group(1)
                score = f"{score_1} - {score_2}"

                team_vs = columns[2].find_element(By.TAG_NAME, "a").text.strip()
                map_name = map_map_name(columns[3].text.strip())

                data["Date"].append(date)
                data["Team VS"].append(team_vs)
                data["Result"].append(score)
                data["Map"].append(map_name)
                data["Match Link"].append(match_link)

            except Exception as inner_e:
                print(f"Внутренняя ошибка парсинга строки: {inner_e}")

    except Exception as e:
        print(f"Ошибка при парсинге матчей игрока {match.group(1)}: {e}")

    return pd.DataFrame(data)


def main():
    df_input_players = pd.read_csv(INPUT_FILE)

    # Названия колонок: Имя, ID, Ссылка
    TIME_RANGE = get_date_from("2023-2024")
    driver = setup_selenium()

    all_matches = []
    for _, row in df_input_players.iterrows():
        try:
            player_name = row["Имя"]
            player_id = row["ID"]
            player_link = row["Ссылка"]

            matches_df = parse_matches(player_link, driver, TIME_RANGE)
            if matches_df.empty:
                continue

            matches_df["Player Name"] = player_name
            matches_df["Player ID"] = player_id
            matches_df["Player Link"] = player_link
            all_matches.append(matches_df)
        except Exception as e:
            print(f"Ошибка обработки игрока {row}: {e}")

    driver.quit()

    if all_matches:
        output_df = pd.concat(all_matches, ignore_index=True)
        column_order = [
            "Player Name",
            "Player ID",
            "Player Link",
            "Date",
            "Team VS",
            "Result",
            "Map",
            "Match Link",
        ]
        output_df = output_df[column_order]
        output_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Файл успешно сохранён: {OUTPUT_FILE}")
    else:
        print("Нет данных для сохранения.")


if __name__ == "__main__":
    main()
