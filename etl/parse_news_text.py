import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from util.selenium_workflow import await_of_load
from util.selenium_workflow import driver_context_manager
from util.csv_workflow import write_links, print_csv
from typing import Dict, List, Union, Tuple
from datetime import datetime
import pandas as pd
import argparse
import os


from logger.logger import Loger
log = Loger(__file__)


OUTPUT_CSV_PATH = "data/raw/last_news_text.csv"
REQUIRED_CSV_PATH = "data/raw/news_links.csv"
PROCESSED_CSV_PATH = "data/raw/news_links_processed.csv"

data_csv_format = {
    "Year": [],
    "Month": [],
    "Date": [],
    "Name": [],
    "Text": [],
    "Link": [],
}

NEWS_TABLE_SELECTOR = (
    "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol"
)
# Для проверки загрузки страницы, парсим таблицу тела новости


def extract_date_news(driver: webdriver) -> Tuple[int, str, int]:
    """
    Захватывает дату нвости с сайта
    """
    # body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > div.news-with-frag-date
    # Для коротких новостных сводок

    # body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.article-info > div.date
    # Для отдлельных новостей
    try:
        try:
            # TODO Настроить парсинг всех дат по отдельности в новостях формата 'https://www.hltv.org/news/41221/short-news-week-12'
            news_time_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > div.news-with-frag-date"
            time_element = driver.find_element(
                By.CSS_SELECTOR, news_time_selector)
            date_in_str = time_element.text
        except:
            # Парсим даты с новости одного дня формата 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
            news_time_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.article-info > div.date"
            time_element = driver.find_element(
                By.CSS_SELECTOR, news_time_selector)
            date_in_str = time_element.text

    except Exception as e:
    # Если не смогли установить дату, то вводим следующие значения
        date_in_str = "1-1-2000 01:01"
        log.prnt(f"Error extracting data and time because of: {e}")
        log.prnt("Will use reserv date!!!")

    date_object = datetime.strptime(date_in_str, "%d-%m-%Y %H:%M")
    current_year = date_object.year
    current_month = date_object.strftime("%B").lower()
    current_date = date_object.day

    return current_year, current_month, current_date


def extract_title_name(driver: webdriver) -> str:
    """
    Забираем название новости
    """
    # body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > h1
    # Для коротких новостных сводок

    # body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > h1
    # Для отдлельных новостей
    title_name = "None"
    try:
        try:
            # TODO Настроить парсинг всех title по отдельности в новостях формата 'https://www.hltv.org/news/41221/short-news-week-12'
            news_title_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > h1"
            title_element = driver.find_element(
                By.CSS_SELECTOR, news_title_selector)
            title_name = title_element.text
        except:
            # Парсим title с новости одного дня формата 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
            news_title_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > h1"
            title_element = driver.find_element(
                By.CSS_SELECTOR, news_title_selector)
            title_name = title_element.text

    except Exception as e:
        log.prnt(f"Error extracting title name because of: {e}")
    return title_name


def extract_news_text(driver: webdriver) -> List[str]:
    """
    Извлекаем данные текста из самой новости по элементам селекторов и абзацам. Внимание: разные селекторы идут не по смысловому порядку (сперва 1 селектор, затем другой)
    """
    # Define the selector for all elements with the required classes
    selectors = [
        ".headertext",
        ".news-block",
        ".featured-quote",
    ]
    text_data = []

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                cleaned_text = re.sub(r"[^\x00-\x7F]+", "", element.text)
                # Чистим текст от всех неизвестных знаков, которых нет в стандарной кодировке

                if cleaned_text:
                    text_data.append(cleaned_text)

        except Exception as e:
            log.prnt(f"Error extracting from selector {selector}: {e}")

    return text_data


def get_all_data_from_news(
    driver: webdriver, link: str
) -> Dict[str, Union[int, str, List[str]]]:
    data = dict()

    current_year, current_month, current_date = extract_date_news(driver)
    title_name = extract_title_name(driver)
    text_data = extract_news_text(driver)

    data["Year"] = current_year
    data["Month"] = current_month
    data["Date"] = current_date
    data["Name"] = title_name
    data["Text"] = text_data
    data["Link"] = link

    return data


def processing_one_news_item(link: str):
    """
    Полная обработка одной новости по ссылке
    """
    with driver_context_manager() as driver_manager:
        driver = driver_manager.driver
        log.prnt(f"Getting data from: {link}")

        driver.get(link)

        isValid = await_of_load(driver, NEWS_TABLE_SELECTOR)
        if isValid:
            log.prnt("Found data")
            cur_data = get_all_data_from_news(driver, link)
            write_links(OUTPUT_CSV_PATH, cur_data, data_csv_format)
        else:
            log.prnt("Cant find data")




def read_links(required_file: str, processed_file: str) -> List[str]:

    if not os.path.exists(required_file):
        log.prnt(f"Cant find Links in {required_file}")
        return []
    

    required_df = pd.read_csv(required_file)
    required_links = set(required_df["link"])

    if os.path.exists(processed_file):
        proc_df = pd.read_csv(processed_file)
        processed_links = set(proc_df["link"])
    else:
        processed_links = set()
    
    links = required_links - processed_links

    return list(links)

def update_links(processed_file: str, links: List[str]) -> None:
    if os.path.exists(processed_file):
        pass
    else:
        empty_df = pd.DataFrame(columns=['link'])
        empty_df.to_csv(processed_file, index=False)
    
    if isinstance(links, str):  # Если links — это строка
        links = [links]

    data_frame = pd.DataFrame(links)
    data_frame.to_csv(processed_file, mode="a", index=False, header=False)
    
    return None

def main(test_mode=False):
    log.prnt("Начали работу с файлом")
    links = read_links(required_file=REQUIRED_CSV_PATH, processed_file=PROCESSED_CSV_PATH)
    for link in links:
        try:
            processing_one_news_item(link)
            update_links(PROCESSED_CSV_PATH, link)
        except Exception as e:
            log.prnt(f"Error in parsing the news with link: {
                     link} ------- {e}")

        if test_mode:
            break

    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # чтобы запустить модуль с флагом --test и это передало True в test_mode
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    main(test_mode=args.test)
    print_csv(OUTPUT_CSV_PATH)
