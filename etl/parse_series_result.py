from selenium.common.exceptions import NoSuchElementException
import argparse
import os
from typing import Optional

import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from util.selenium_workflow import await_of_load, driver_context_manager

INPUT_CSV_PATH = "data/processed/matches_cleaned.csv"
OUTPUT_CSV_PATH = "data/processed/series_results.csv"
SERIES_DIV_SELECTOR = ".columns"


def prepare_dataframe(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    cols = ["team_id", "team_name", "opponents_id", "date", "match_link"]
    df2 = df[cols].copy()
    df2["series_link"] = None
    df2["series_result"] = None
    return df2


def process_row(
    row: pd.Series, driver: uc.Chrome, index: Optional[int] = None
) -> pd.Series:
    link = row["match_link"]
    driver.get(link)

    try:
        print("try bo3/bo5 logic")
        parent_element = driver.find_element(
            By.CSS_SELECTOR, SERIES_DIV_SELECTOR)
        a = parent_element.find_element(By.CSS_SELECTOR, "a.col:nth-child(1)")
        row["series_link"] = a.get_attribute("href")
        row["series_result"] = parent_element.find_element(
            By.CSS_SELECTOR,
            "a.col:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)",
        ).text.strip()
        print("bo3/bo5 успешно обработан")
        return row

    except NoSuchElementException as e:
        print("bo3/bo5 не найден, пробуем bo1...", e)

        try:
            team_left = driver.find_element(By.CSS_SELECTOR, ".team-left")
            team_left_name = team_left.find_element(By.TAG_NAME, "img").get_attribute(
                "alt"
            )
            team_left_w_or_l = (
                "W"
                if team_left.find_element(By.TAG_NAME, "div").get_attribute("class")
                == "bold won"
                else "L"
            )

            match ((team_left_w_or_l == "W"), (team_left_name == row["team_name"])):
                case (True, True):
                    row["series_result"] = "1:0"
                case (True, False):
                    row["series_result"] = "0:1"
                case (False, True):
                    row["series_result"] = "0:1"
                case (False, False):
                    row["series_result"] = "1:0"

            print("bo1 успешно обработан")
            return row

        except Exception as inner_e:
            print("Ошибка при обработке bo1:", inner_e)
            return row  # или пробросить ошибку, если нужно

    except Exception as other:
        print("Неизвестная ошибка при обработке:", other)
        return row


def main(test_mode: bool = False):
    if test_mode:
        print("TEST MODE IS ENABLED\nPROCESSING ONLY 1 ROW")
        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            data = {
                "team_id": [6667],
                "opponent_id": [5995],
                "date": ["13/12/24"],
                "match_link": [
                    "https://www.hltv.org/stats/matches/mapstatsid/189558/g2-vs-heroic"
                ],
                "series_link": [None],
                "series_result": [None],
            }
            row = pd.DataFrame(data).iloc[0]
            result_row = process_row(row, driver)
            print(result_row)
            return

    # Загружаем данные
    if not os.path.exists(OUTPUT_CSV_PATH):
        print("Файл результатов не найден. Создаём с нуля...")
        df = prepare_dataframe(INPUT_CSV_PATH)
        # Создаём пустой файл с заголовками
        df.iloc[0:0].to_csv(OUTPUT_CSV_PATH, index=False)
        processed_links = set()
    else:
        processed_df = pd.read_csv(OUTPUT_CSV_PATH)
        processed_links = set(processed_df["match_link"].tolist())

    full_df = pd.read_csv(INPUT_CSV_PATH)
    unprocessed_df = full_df[~full_df["match_link"].isin(processed_links)]

    if unprocessed_df.empty:
        print("Все строки уже обработаны.")
        return

    print(f"Начинаем обработку {len(unprocessed_df)} строк...")

    for index, row in unprocessed_df.iterrows():
        try:
            with driver_context_manager() as driver_manager:
                driver = driver_manager.driver
                extended_row = {
                    **row.to_dict(),
                    "series_link": None,
                    "series_result": None,
                }
                row_series = pd.Series(extended_row)
                result_row = process_row(row_series, driver, index)

                pd.DataFrame([result_row]).to_csv(
                    OUTPUT_CSV_PATH,
                    mode="a",
                    header=not os.path.exists(OUTPUT_CSV_PATH)
                    or os.path.getsize(OUTPUT_CSV_PATH) == 0,
                    index=False,
                )
        except Exception as e:
            print(f"Ошибка при обработке строки {index}: {e}")
            print("Останавливаем парсинг. Вы можете перезапустить позже.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
