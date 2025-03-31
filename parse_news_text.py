import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from util.selenium_workflow import await_of_load
from util.selenium_workflow import driver_context_manager, await_of_load
from util.csv_workflow import write_links
from typing import Dict, List, Union


output_file = "Data/raw/last_news_links.txt"

data_csv_format = {
            "Year": [],
            "Month": [],
            "Date": [],
            "Name": [],
            "Text": [],
            "Link": []
    }

# body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > div.news-with-frag-date
def extract_news(driver: webdriver) -> Dict[str, Union[int, str, List[str]]]:
    data = data_csv_format
    news_time_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.news-with-frag-head-container > div > div > div.news-with-frag-date"
    time_element = driver.find_element(By.CSS_SELECTOR, news_time_selector)
    print(time_element.text)
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
            print(f"Error extracting from selector '{selector}': {e}")
    print(text_data)
    return text_data



def main():

    #link = 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
    link = 'https://www.hltv.org/news/41221/short-news-week-12'

    with driver_context_manager() as driver_manager:
        driver = driver_manager.driver
        
        print(f"Getting data from: {link}")
        driver.get(link)

        selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article"
        isValid = await_of_load(driver, selector)
        if isValid:
            print("Found data")
            cur_data = extract_news(driver)
            #write_links(output_file, cur_data, data_csv_format)
        else:
            print("Cant find data")


if __name__ == "__main__":
    main()