from datetime import datetime
from typing import Dict, List, Union
import pandas as pd
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By

from logger.logger import Loger
from util.csv_workflow import write_links, get_last_date
from util.datetime_util import generate_date_list_every_week, generate_date_list
from util.selenium_workflow import await_of_load, driver_context_manager

log = Loger(__file__)


URL = "https://www.hltv.org/ranking/teams"
OUTPUT_FILE = "data/raw/team_ranking.csv"

data_csv_format = {
    "Year": [],
    "Month": [],
    "Date": [],
    "Rank": [],
    "Name_of_team": [],
    "HLTV_points": [],
    "Members": [],
    "Link": [],
}


TABLE_SELECTOR = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking"
# Селектор общей таблицы данных


def extract_data(
    url: str, driver: webdriver
) -> Dict[str, Union[str, int, List[Dict[str, str]]]]:
    _, cur_year, cur_month, cur_date = url.split("/")
    data = data_csv_format

    try:
        parent_elements = get_team_blocks(driver)

        for index, element in enumerate(parent_elements, start=1):
            if index < 4:
                continue

            try:
                team_info = extract_team_info(element)
                players = extract_players(element)

                data["Year"].append(cur_year)
                data["Month"].append(cur_month)
                data["Date"].append(cur_date)
                data["Rank"].append(team_info["position"])
                data["Name_of_team"].append(team_info["team_name"])
                data["HLTV_points"].append(team_info["hltv_points"])
                data["Members"].append(players)
                data["Link"].append(team_info["team_link"])

            except Exception as e:
                log.prnt(f"Ошибка при обработке команды: {e}")

    except Exception as e:
        log.prnt(f"Ошибка при извлечении блока команд: {e}")

    return data


def get_team_blocks(driver: webdriver):
    return driver.find_elements(
        By.CSS_SELECTOR,
        "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking > div:nth-child(1) > div",
    )


def extract_team_info(element) -> Dict[str, str]:
    position = element.find_element(
        By.CSS_SELECTOR, "div > div.ranking-header > span.position"
    ).text

    team_link = element.find_element(
        By.CSS_SELECTOR, "div > div.lineup-con > div > a:nth-child(1)"
    ).get_attribute("href")

    try:
        name_elem = element.find_element(
            By.CSS_SELECTOR,
            "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers.teamLineExpanded > span.name",
        )
        points_elem = element.find_element(
            By.CSS_SELECTOR,
            "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers.teamLineExpanded > span.points",
        )
    except:
        name_elem = element.find_element(
            By.CSS_SELECTOR,
            "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers > span.name",
        )
        points_elem = element.find_element(
            By.CSS_SELECTOR,
            "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers > span.name",
        )

    return {
        "position": position,
        "team_name": name_elem.text,
        "hltv_points": points_elem.text,
        "team_link": team_link,
    }


def extract_players(element) -> Dict[str, str]:
    players = dict()
    player_cells = element.find_elements(
        By.CSS_SELECTOR, "div > div.lineup-con > table > tbody > tr > td"
    )
    count = len(player_cells)

    for i in range(count):
        try:
            player_link = element.find_element(
                By.CSS_SELECTOR,
                f"div > div.lineup-con > table > tbody > tr > td:nth-child({
                    i + 1
                }) > a",
            )
        except:
            player_link = element.find_element(
                By.CSS_SELECTOR,
                f"div > div.lineup-con.hidden > table > tbody > tr > td:nth-child({
                    i + 1
                }) > a",
            )

        link = player_link.get_attribute("href")
        name = player_link.find_element(By.CSS_SELECTOR, "img").get_attribute("alt")

        players[f"Name_player_{i + 1}"] = name
        players[f"Link_player_{i + 1}"] = link

    return players


def get_required_links(output_file: str) -> List[str]:
    # urls = generate_date_list_every_week(start_date, end_date)

    start_date = max(datetime(2023, 1, 2), get_last_date(output_file))
    log.prnt(f"Start parsing from {start_date}")
    end_date = datetime.today()
    urls = generate_date_list(start_date, end_date)

    for ind, cur_url in enumerate(urls):
        log.prnt(str("Finding data from: " + URL + cur_url))
        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            driver.get(str(URL + cur_url))

            isValid = await_of_load(driver, TABLE_SELECTOR)
            if isValid:
                log.prnt("Found valid link start parse every week")
                urls = urls[ind::7]  # начинаем искать каждую неделю
                break
    return urls


def update_links(
    processed_file: str,
    data: Dict[str, Union[str, int, List[Dict[str, str]]]],
    format: Dict[str, Union[str, int, List[Dict[str, str]]]] = data_csv_format,
) -> None:
    import os

    key_columns = ["Year", "Month", "Date", "Rank"]

    if os.path.exists(processed_file):
        processed_df = pd.read_csv(processed_file)
    else:
        empty_df = pd.DataFrame(columns=format.keys())
        empty_df.to_csv(processed_file, index=False)
        processed_df = empty_df

    try:
        data_frame = pd.DataFrame(data)

        processed_df["Year"] = processed_df["Year"].astype(int)
        data_frame["Year"] = data_frame["Year"].astype(int)
        processed_df["Month"] = processed_df["Month"].astype(str)
        data_frame["Month"] = data_frame["Month"].astype(str)
        processed_df["Date"] = processed_df["Date"].astype(int)
        data_frame["Date"] = data_frame["Date"].astype(int)

        if not processed_df.empty:
            data_frame = data_frame.merge(
                processed_df[key_columns], on=key_columns, how="left", indicator=True
            )
            data_frame = data_frame[data_frame["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )
            # data_frame = data_frame[~data_frame["link"].isin(processed_df["link"])]

        if not data_frame.empty:
            data_frame.to_csv(processed_file, mode="a", index=False, header=False)
            print(f"Добавлено {len(data_frame)} новых строк в {processed_file}")
        else:
            print("Новых строк нет — ничего не добавлено.")
    except pd.errors.ParserError as e:
        log.prnt(f"Parser error: {e}")
    return None


def one_iter_full_work(driver: webdriver, batch: List[str]):
    valids = False
    for cur_url in batch:
        log.prnt(str("Getting data from: " + URL + cur_url))
        try:
            driver.get(str(URL + cur_url))

            isValid = await_of_load(driver, TABLE_SELECTOR)
            if isValid:
                log.prnt("Extracting data")
                cur_data = extract_data(cur_url, driver)
                log.prnt("Writing data")
                update_links(OUTPUT_FILE, cur_data, data_csv_format)
                valids = True
            else:
                log.prnt("Cant find data")
        except Exception as e:
            log.prnt(f"Error processing URL: {URL + cur_url}\nException: {e}")
            continue

    return valids


def main(test_mode=False):
    log.prnt("Начали работу с файлом")
    valids = False
    batch_size = 90

    urls = get_required_links(OUTPUT_FILE)
    for i in range(0, len(urls), batch_size):
        batch = urls[i : i + batch_size]

        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            valids = one_iter_full_work(driver=driver, batch=batch)

        if test_mode and valids:
            break
    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # чтобы запустить модуль с флагом --test и это передало True в test_mode
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
