import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import argparse
from util.setup_selenium import setup_selenium
from typing import Tuple, Set

from logger.logger import Loger
log = Loger(__file__)


PROCESSED_FILE = "data/processed/matches_parsed.csv"
INPUT_FILE = "data/processed/matches.csv"


def parse_round_results(match_link, driver):
    """Парсит результаты раундов по указанной ссылке."""
    driver.get(match_link)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.round-history-team-row"))
    )
    rounds = driver.find_elements(
        By.CSS_SELECTOR, "div.round-history-team-row:nth-child(1) > img"
    )
    round_1 = rounds[3]
    round_13 = rounds[15]

    # print(round_1.get_attribute("src"))

    def is_round_win(round_element):
        return (
            round_element.get_attribute("src")
            != "https://www.hltv.org/img/static/scoreboard/emptyHistory.svg"
        )

    round_1_win = is_round_win(round_1)
    round_13_win = is_round_win(round_13)
    return round_1_win, round_13_win


def load_matches() -> Tuple[pd.DataFrame, Set[str], pd.DataFrame]:
    """Загружает все матчи и возвращает: (df_matches, обработанные ссылки, df_processed)"""
    if not os.path.exists(INPUT_FILE):
        log.prnt(f"Ошибка, не нашли {INPUT_FILE}")
        empty_df = pd.DataFrame()
        return empty_df, set(), empty_df
    
    df_matches = pd.read_csv(INPUT_FILE)

    if os.path.exists(PROCESSED_FILE):
        df_processed = pd.read_csv(PROCESSED_FILE)
        processed_links = set(df_processed["match_link"].unique())
    else:
        df_processed = pd.DataFrame(columns=list(df_matches.columns) + ["round_1_win", "round_15_win"])
        processed_links = set()

    return df_matches, processed_links, df_processed


def save_processed_row(row: pd.Series) -> None:
    """Сохраняет одну строку в файл обработанных матчей"""
    header_needed = not os.path.exists(PROCESSED_FILE)
    row.to_frame().T.to_csv(PROCESSED_FILE, mode="a", index=False, header=header_needed)


def process_match(row: pd.Series, driver) -> pd.Series:
    """Обрабатывает один матч и возвращает обновлённую строку"""
    match_link = row["match_link"]
    try:
        round_1_win, round_13_win = parse_round_results(match_link, driver)
        row["round_1_win"] = round_1_win
        row["round_15_win"] = round_13_win
        log.prnt(f"Успешно обработали {match_link}")
    except Exception as e:
        log.prnt(f"Ошибка при парсинге {match_link}: {e}")
        row["round_1_win"] = None
        row["round_15_win"] = None
    return row


def main(test_mode = False):
    log.prnt("Начали работу с файлом")

    df_matches, processed_links, _ = load_matches()
    driver = setup_selenium()

    for _, row in df_matches.iterrows():
        match_link = row["match_link"]

        if match_link in processed_links: # Скипаем обработанные ссылки
            continue

        updated_row = process_match(row, driver)
        save_processed_row(updated_row)
        processed_links.add(match_link)
        if test_mode:
            break
    driver.quit()

    log.prnt("Файл matches_parsed.csv успешно обновлён!")
    log.prnt("Закончили работу с файлом")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # чтобы запустить модуль с флагом --test и это передало True в test_mode
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
