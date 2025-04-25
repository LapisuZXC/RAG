import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.setup_selenium import setup_selenium


from logger.logger import Loger
log = Loger(__file__)



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


def main(TEST_MODE = False):
    log.prnt("Начали работу с файлом")

    # Заменить на unique_teams.csv
    df_teams = pd.read_csv("data/processed/unique_teams.csv")
    driver = setup_selenium()

    all_maps_data = []

    for _, row in df_teams.iterrows():
        team_id = row["team_id"]
        team_name = row["team_name"]

        log.prnt(f"Парсинг команды: {team_name} (ID: {team_id})")

        try:
            team_maps = parse_team_maps(team_id, team_name, driver)
            all_maps_data.extend(team_maps)
        except Exception as e:
            log.prnt(f"Ошибка при парсинге команды {team_name}: {e}")
        

        if TEST_MODE:
            break


    driver.quit()

    df_maps = pd.DataFrame(
        all_maps_data,
        columns=["team_id", "team_name", "map_name", "winrate", "pickrate", "banrate"],
    )
    df_maps.to_csv("data/processed/team_maps.csv", index=False)
    log.prnt("Файл team_maps.csv успешно создан!")

    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    main()
