import os
import pandas as pd
import argparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.datetime_util import get_date_from
from util.setup_selenium import setup_selenium


from logger.logger import Loger
log = Loger(__file__)



TIME_FILTER = get_date_from(time_filter="2023-2024")


def parse_team_matches(team_id, team_name, driver):
    # G2,5995
    # https://www.hltv.org/stats/teams/matches/5995/G2
    url = (
        f"https://www.hltv.org/stats/teams/matches/{team_id}/{team_name}"
        + "?"
        + TIME_FILTER
    )
    driver.get(url)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
    )  # Ожидание загрузки данных

    matches = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    current_event = None
    for i, row in enumerate(rows):
        # !!!!
        cells = row.find_elements(By.TAG_NAME, "td")
        date = cells[0].text.strip()
        link_elements = row.find_elements(By.CSS_SELECTOR, "td:nth-child(1) > a")
        link = link_elements[0].get_attribute("href") if link_elements else None
        event = cells[1].text.strip()
        opponent = cells[3].text.strip()
        map_played = cells[4].text.strip()
        result = cells[5].text.strip()
        win_loss = cells[6].text.strip()
        current_event = event  # Запоминаем турнир

        matches.append(
            [
                team_name,
                date,
                current_event,
                opponent,
                map_played,
                result,
                win_loss,
                link,
            ]
        )

    return matches


# def main(test_mode = False):
#     log.prnt("Начали работу с файлом")

#     # Заменить на unique_teams.csv
#     df_teams = pd.read_csv("data/processed/unique_teams.csv")
#     driver = setup_selenium()

#     all_matches = []

#     for _, row in df_teams.iterrows():
#         team_id = row["team_id"]
#         team_name = row["team_name"].replace(" ", "-").lower()
#         log.prnt(f"Парсим {team_name}...")

#         try:
#             matches = parse_team_matches(team_id, team_name, driver)
#             all_matches.extend(matches)
#         except Exception as e:
#             log.prnt(f"Ошибка при парсинге {team_name}: {e}")
        
        
#         if test_mode:
#             break


#     driver.quit()

#     df_matches = pd.DataFrame(
#         all_matches,
#         columns=[
#             "team_name",
#             "date",
#             "event",
#             "opponent",
#             "map",
#             "result",
#             "win_loss",
#             "match_link",
#         ],
#     )

#     # Убираем лишние символы из team_name
#     df_matches["team_name"] = df_matches["team_name"].apply(lambda x: x.strip("[]'"))

#     df_matches.to_csv("data/processed/matches.csv", index=False)
#     log.prnt("Файл matches.csv успешно сохранён!")
#     log.prnt("Закончили работу с файлом")

# --- Загрузка уже обработанных команд ---
def load_parsed_teams(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

# --- Сохранение имени успешно обработанной команды ---
def save_parsed_team(filepath, team_name):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(team_name + "\n")

# --- Загрузка уже собранных матчей (если есть) ---
def load_existing_matches(filepath):
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame(columns=[
        "team_name", "date", "event", "opponent", "map",
        "result", "win_loss", "match_link"
    ])

# --- Обработка одной команды ---
def process_team(team_id, team_name_raw, driver):
    team_name = team_name_raw.replace(" ", "-").lower()
    log.prnt(f"Парсим {team_name}...")
    matches = parse_team_matches(team_id, team_name, driver)
    df = pd.DataFrame(matches, columns=[
        "team_name", "date", "event", "opponent", "map",
        "result", "win_loss", "match_link"
    ])
    df["team_name"] = df["team_name"].apply(lambda x: x.strip("[]'"))
    return df, team_name

# --- Главная функция ---
def main(test_mode=False):
    log.prnt("Начали работу с файлом")

    df_teams = pd.read_csv("data/processed/unique_teams.csv")
    parsed_teams_file = "data/processed/parsed_teams.txt"
    matches_file = "data/processed/matches.csv"

    parsed_teams = load_parsed_teams(parsed_teams_file)
    df_matches = load_existing_matches(matches_file)

    

    for _, row in df_teams.iterrows():
        driver = setup_selenium()
        team_id = row["team_id"]
        team_name_raw = row["team_name"]
        team_name_formatted = team_name_raw.replace(" ", "-").lower()

        if team_name_formatted in parsed_teams:
            driver.quit()
            continue

        try:
            df_new_matches, team_name_formatted = process_team(team_id, team_name_raw, driver)
            df_matches = pd.concat([df_matches, df_new_matches], ignore_index=True)

            # Сохраняем результаты
            df_matches.to_csv(matches_file, index=False)
            save_parsed_team(parsed_teams_file, team_name_formatted)
            log.prnt(f"{team_name_formatted} успешно обработан и сохранён.")

        except Exception as e:
            log.prnt(f"Ошибка при парсинге {team_name_formatted}: {e}")

        driver.quit()

        if test_mode:
            break

    
    log.prnt("Закончили работу с файлом")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # чтобы запустить модуль с флагом --test и это передало True в test_mode
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
