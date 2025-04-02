import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from util.selenium_workflow import await_of_load
from util.selenium_workflow import driver_context_manager, await_of_load
from util.csv_workflow import write_links, print_csv
from typing import Dict, List, Union, Tuple
from datetime import datetime

output_file = "data/raw/last_news_text.csv"
input_file = "data/raw/news_links.txt"

data_csv_format = {
            "Year": [],
            "Month": [],
            "Date": [],
            "Name": [],
            "Text": [],
            "Link": []
    }

NEWS_TABLE_SELECTOR = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol"
#Для проверки загрузки страницы, парсим таблицу тела новости



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
            time_element = driver.find_element(By.CSS_SELECTOR, news_time_selector)
            date_in_str = time_element.text
        except:
            # Парсим даты с новости одного дня формата 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
            news_time_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.article-info > div.date"
            time_element = driver.find_element(By.CSS_SELECTOR, news_time_selector)
            date_in_str = time_element.text
            
    except Exception as e:
        date_in_str = "1-1-2000 01:01" # Если не смогли установить дату, то вводим следующие значения
        print(f"Error extracting data and time because of: {e}")
        print("Will use reserv date!!!")
    
    date_object = datetime.strptime(date_in_str, "%d-%m-%Y %H:%M")
    current_year = date_object.year
    current_month = date_object.strftime("%B").lower()
    current_date = date_object.day

    return current_year, current_month, current_date


def extract_title_name(driver: webdriver) -> str:
    """
    Забираем название новости
    """
    #body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > h1
    # Для коротких новостных сводок

    #body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > h1
    # Для отдлельных новостей
    title_name = "None"
    try:
        try:
            # TODO Настроить парсинг всех title по отдельности в новостях формата 'https://www.hltv.org/news/41221/short-news-week-12'
            news_title_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > h1"
            title_element = driver.find_element(By.CSS_SELECTOR, news_title_selector)
            title_name = title_element.text
        except:
            # Парсим title с новости одного дня формата 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
            news_title_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > h1"
            title_element = driver.find_element(By.CSS_SELECTOR, news_title_selector)
            title_name = title_element.text
            
    except Exception as e:
        print(f"Error extracting title name because of: {e}")
    
    return title_name


def extract_news_text(driver: webdriver) -> List[str]:
    """
    Извлекаем данные текста из самой новости по элементам селекторов и абзацам. Внимание: разные селекторы идут не по смысловому порядку (сперва 1 селектор, затем другой)
    """
    # Define the selector for all elements with the required classes
    selectors = [
        '.headertext',
        '.news-block',
        '.featured-quote',
    ]
    text_data = []

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                cleaned_text = re.sub(r'[^\x00-\x7F]+', '', element.text)
                # Чистим текст от всех неизвестных знаков, которых нет в стандарной кодировке
                
                if cleaned_text:
                    text_data.append(cleaned_text)

        except Exception as e:
            print(f"Error extracting from selector {selector}: {e}")

    return text_data
    

def get_all_data_from_news(driver: webdriver, link: str) -> Dict[ str, Union[int, str, List[str]] ]:
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
    Полная обработка и запись одной новости по ссылке
    """
    with driver_context_manager() as driver_manager:
        driver = driver_manager.driver
        
        print(f"Getting data from: {link}")
        driver.get(link)

        isValid = await_of_load(driver, NEWS_TABLE_SELECTOR)
        if isValid:
            print("Found data")
            cur_data = get_all_data_from_news(driver, link)
            write_links(output_file, cur_data, data_csv_format)
        else:
            print("Cant find data")


def read_links() -> list[str]:
    try:
        with open(input_file, 'r') as file:
            links = file.readlines()
    except Exception as e:
        print(f"Error in reading input_file: {input_file} --------- {e}")
        links = []
    return links



def main():

    links = read_links()
    for link in links[:2]:
        try:
            processing_one_news_item(link)
        except Exception as e:
            print(f"Error in parsing the news with link: {link} ------- {e}")


if __name__ == "__main__":
    main()
    print_csv(output_file)