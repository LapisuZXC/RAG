from selenium import webdriver
from selenium.webdriver.common.by import By
from util.selenium_workflow import await_of_load, driver_context_manager
from util.datetime_util import generate_month_list


from logger.logger import Loger
log = Loger(__file__)



URL = 'https://www.hltv.org/news/archive/'
output_file = "data/raw/news_links.txt"

TABLE_SELECTOR = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol"
# Селектор общей таблицы данных



def extract_links(driver: webdriver) -> list[str]:
    parent_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.index > div.standard-box.standard-list"
    links = []

    try:
        link_elements = driver.find_elements(By.CSS_SELECTOR, f"{parent_selector} > a")
        for link_element in link_elements:
            link = link_element.get_attribute('href')
            if link:
                links.append(link)
    except Exception as e:
        log.prnt(f"Error extracting links: {e}")
    
    return links


def write_links(output_file: str, data: {str}):
    with open(output_file, 'w') as file:
        for month in data:
            for link in month:
                file.write(link + '\n')
    log.prnt(f"Data written to {output_file}")



def main():
    log.prnt("Начали работу с файлом")


    required_monthes = generate_month_list(2)
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
                links.append(extract_links(driver))
            else:
                log.prnt("Cant find data")

    log.prnt("Начинаем запись с помощью write_links")
    write_links(output_file, links)

    log.prnt("Закончили работу с файлом")


if __name__ == "__main__":
    main()