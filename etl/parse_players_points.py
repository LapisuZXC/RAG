from selenium.common.exceptions import NoSuchElementException
import argparse
import os
from typing import Optional

import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from util.selenium_workflow import driver_context_manager

INPUT_CSV_PATH = "data/processed/unique_players.csv"
OUTPUT_CSV_PATH = "data/processed/players_points.csv"
HLTV_POINTS_SELECTOR = (
    "div.player-stat:nth-child(1) > span:nth-child(2) > p:nth-child(1)"
)


def prepare_dataframe(input_path: str) -> pd.DataFrame:
    """
    Подготавливает датафрейм с нужными колонками.
    Если файл уже существует, он не будет создан заново.
    """
    df = pd.read_csv(input_path)
    df["HLTV_points"] = None
    return df


def process_row(
    row: pd.Series, driver: uc.Chrome, index: Optional[int] = None
) -> pd.Series:
    """
    Обрабатывает одну строку: переходит по ссылке игрока и достаёт HLTV points.
    Возвращает обновлённую строку.
    """
    nickname: str = row["Nickname"]
    player_id = row["Player ID"]
    link = f"https://www.hltv.org/player/{player_id}/{nickname.lower()}"
    driver.get(link)

    try:
        print(f"[{index}] Поиск HLTV points для {nickname}...")
        points = driver.find_element(By.CSS_SELECTOR, HLTV_POINTS_SELECTOR)
        row["HLTV_points"] = points.text.strip()
        print(f"[{index}] Найдено: {row['HLTV_points']}")
        return row
    except NoSuchElementException as e:
        print(f"[{index}] Элемент не найден: {e}")
        return row
    except Exception as e:
        print(f"[{index}] Неизвестная ошибка: {e}")
        return row


def main(test_mode: bool = False) -> None:
    if test_mode:
        print("TEST MODE ENABLED — обработка только одной строки")
        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            data = {"Nickname": ["cadiaN"], "Player ID": ["7964"]}
            row = pd.DataFrame(data).iloc[0]
            result_row = process_row(row, driver)
            print(result_row)
            return

    # Если файла с результатами нет, создаём с нуля
    if not os.path.exists(OUTPUT_CSV_PATH):
        print("Файл результатов не найден. Создаём новый.")
        df = prepare_dataframe(INPUT_CSV_PATH)
        df.iloc[0:0].to_csv(OUTPUT_CSV_PATH, index=False)
        processed_ids = set()
    else:
        processed_df = pd.read_csv(OUTPUT_CSV_PATH)
        processed_ids = set(processed_df["Player ID"].tolist())

    full_df = pd.read_csv(INPUT_CSV_PATH)
    unprocessed_df = full_df[~full_df["Player ID"].isin(processed_ids)]

    if unprocessed_df.empty:
        print("Все игроки уже обработаны.")
        return

    print(f"Начинаем обработку {len(unprocessed_df)} строк...")

    for index, row in unprocessed_df.iterrows():
        try:
            with driver_context_manager() as driver_manager:
                driver = driver_manager.driver
                row["HLTV_points"] = None  # инициализация
                result_row = process_row(row, driver, index)

                pd.DataFrame([result_row]).to_csv(
                    OUTPUT_CSV_PATH,
                    mode="a",
                    header=not os.path.exists(OUTPUT_CSV_PATH)
                    or os.path.getsize(OUTPUT_CSV_PATH) == 0,
                    index=False,
                )
        except Exception as e:
            print(f"Ошибка при обработке строки {index}: {e}")
            print("Парсинг остановлен. Перезапустите позже при необходимости.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
