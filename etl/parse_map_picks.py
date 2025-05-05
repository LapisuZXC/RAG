import pandas as pd
import os
import argparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.setup_selenium import setup_selenium


from logger.logger import Loger
log = Loger(__file__)

PROCESSED_FILE = "data/processed/team_maps.csv"


def parse_team_maps(team_id, team_name, driver):
    """Парсит мап пики для указанной команды."""
    url = f"https://www.hltv.org/stats/teams/maps/{team_id}/{team_name.lower()}"
    log.prnt(f"Открываю URL: {url}")
    driver.get(url)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.two-grid:nth-child(9)"))
    )

    maps_data = []

    for i in range(1, 12):
        try:
            map_name_elem = driver.find_element(
                By.CSS_SELECTOR,
                f"div.two-grid:nth-child(9) > div:nth-child({
                    i
                }) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1) > div:nth-child(2)",
            )
            map_name = map_name_elem.text.strip()
            log.prnt(f"Найдена карта: {map_name}")

            if map_name in ["Cache", "Cobblestone"]:
                log.prnt(f"Пропускаю карту {map_name}, так как она устарела.")
                continue

            winrate_elem = driver.find_element(
                By.CSS_SELECTOR,
                f"div.two-grid:nth-child(9) > div:nth-child({
                    i
                }) > div:nth-child(2) > div:nth-child(2) > span:nth-child(2)",
            )
            winrate = winrate_elem.text.strip()
            log.prnt(f"Винрейт карты {map_name}: {winrate}")

            pickrate_elem = driver.find_element(
                By.CSS_SELECTOR,
                f"div.two-grid:nth-child(9) > div:nth-child({
                    i
                }) > div:nth-child(2) > div:nth-child(6) > span:nth-child(2)",
            )
            pickrate = pickrate_elem.text.strip()
            log.prnt(f"Пикрейт карты {map_name}: {pickrate}")

            banrate_elem = driver.find_element(
                By.CSS_SELECTOR,
                f"div.two-grid:nth-child(9) > div:nth-child({
                    i
                }) > div:nth-child(2) > div:nth-child(7) > span:nth-child(2)",
            )
            banrate = banrate_elem.text.strip()
            log.prnt(f"Банрейт карты {map_name}: {banrate}")

            maps_data.append((team_id, team_name, map_name, winrate, pickrate, banrate))
        except Exception as e:
            log.prnt(f"Ошибка при парсинге карты {i} для {team_name}: {e}")

    return maps_data



def save_team_maps(team_maps, filepath="data/processed/team_maps.csv"):
    df = pd.DataFrame(
        team_maps,
        columns=["team_id", "team_name", "map_name", "winrate", "pickrate", "banrate"],
    )
    df.to_csv(filepath, mode='a', index=False, header=not os.path.exists(filepath))


def load_processed_ids(filepath="data/processed/team_maps.csv"):
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            return set(df["team_id"].unique())
        except Exception:
            return set()
    return set()


def walk_through_one(team_id, team_name, driver, processed_ids_file="data/processed/team_maps.csv"):

    if team_id in load_processed_ids(processed_ids_file):
        log.prnt(f"Пропуск {team_name} (ID: {team_id}) — уже обработан")
        return None

    log.prnt(f"Парсинг команды: {team_name} (ID: {team_id})")

    try:
        team_maps = parse_team_maps(team_id, team_name, driver)
        save_team_maps(team_maps, processed_ids_file)
        log.prnt(f"Данные для {team_name} сохранены.")
        return team_maps
    except Exception as e:
        log.prnt(f"Ошибка при парсинге команды {team_name}: {e}")
        return None


def main(test_mode=False):
    log.prnt("Начали работу с файлом")

    df_teams = pd.read_csv("data/processed/unique_teams.csv")
    processed_ids_file = "data/processed/team_maps.csv"
    processed_ids = load_processed_ids(processed_ids_file)

    driver = setup_selenium()

    for _, row in df_teams.iterrows():
        team_id = row["team_id"]
        team_name = row["team_name"]

        walk_through_one(team_id, team_name, driver, processed_ids_file)

        if test_mode:
            break

    driver.quit()
    log.prnt("Закончили работу с файлом")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # чтобы запустить модуль с флагом --test и это передало True в test_mode
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
