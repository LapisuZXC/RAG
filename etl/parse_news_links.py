from selenium import webdriver
from selenium.webdriver.common.by import By
from util.selenium_workflow import await_of_load, driver_context_manager
from util.datetime_util import generate_month_list
import pandas as pd
from typing import Dict, List, Union

from logger.logger import Loger
log = Loger(__file__)



URL = 'https://www.hltv.org/news/archive/'
OUTPUT_CSV_PATH = "data/raw/news_links.csv"



TABLE_SELECTOR = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol"
# Селектор общей таблицы данных

DATE_SELECTOR = f"body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.index > div:nth-child(4) > a:nth-child({13}) > div.newstc > div.newsrecent"


def extract_links(driver: webdriver) -> list[str]:
    parent_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.index > div.standard-box.standard-list"
    data = []

    try:
        link_elements = driver.find_elements(By.CSS_SELECTOR, f"{parent_selector} > a")
        date_elements = driver.find_elements(By.CSS_SELECTOR, f"{parent_selector} > a > div.newstc > div.newsrecent")
        for link_atr, date_atr in zip(link_elements, date_elements):
            link = link_atr.get_attribute('href')
            date = date_atr.text
            if link:
                data.append({"date": date, "link": link})
    except Exception as e:
        log.prnt(f"Error extracting links: {e}")
    
    return data



def append_csv(output_file: str, data: List[Dict[str, str]]) -> None:
    import os

    if os.path.exists(output_file):
        processed_df = pd.read_csv(output_file)
    else:
        empty_df = pd.DataFrame(columns=['date', 'link'])
        empty_df.to_csv(output_file, index=False)
        processed_df = empty_df

    data_frame = pd.DataFrame(data)

    if not processed_df.empty:
        data_frame = data_frame[~data_frame["link"].isin(processed_df["link"])]

    if not data_frame.empty:
        data_frame.to_csv(output_file, mode="a", index=False, header=False)
        print(f"Добавлено {len(data_frame)} новых строк в {output_file}")
    else:
        print("Новых строк нет — ничего не добавлено.")
    
    return None


def main():
    log.prnt("Начали работу с файлом")


    required_monthes = generate_month_list(3)
    links = []

    for current_month in required_monthes:
        cur_url = str(URL + current_month)
        
        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            log.prnt(f"Parsing news list from: {cur_url}")

            driver.get(cur_url)
            isValid = await_of_load(driver, TABLE_SELECTOR)

            if isValid:
                log.prnt("Found data")
                links.extend(extract_links(driver))
            else:
                log.prnt("Cant find data")

    log.prnt("Начинаем запись с помощью write_links")
    append_csv(output_file = OUTPUT_CSV_PATH, data = links)

    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    main()