import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth




# URL страницы
URL = 'https://www.hltv.org/news/archive/'
# Путь файла записи
output_file = "Data/news_links.txt"



def last_three_months():
    today = datetime.now()
    last_months = []

    for i in range(0, 1):
        month_date = today - relativedelta(months=i)
        month_str = month_date.strftime("%Y/%B").lower()
        last_months.append(month_str)

    return last_months[::-1]



def setup_selenium() -> "driver":
    # Настройка Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Запуск в фоновом режиме
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Инициализация драйвера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    # Настройка Selenium Stealth
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def await_of_load() -> bool:
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol")))
        print("Таблица загружена.")
        return True
    
    except Exception as e:
        print(f"Ошибка при загрузке таблицы: {e}")
        return False



def extract_data(url: str) -> [str]:
    # Define the base selector for the parent container of the links
    parent_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.index > div.standard-box.standard-list"
    links = []

    try:
        link_elements = driver.find_elements(By.CSS_SELECTOR, f"{parent_selector} > a")
        for index, link_element in enumerate(link_elements):
            if index > 101:
                break
            link = link_element.get_attribute('href')
            if link:
                links.append(link)
    except Exception as e:
        print(f"Error extracting links: {e}")
    
    return links


def write_links(output_file: str, data: {str}) -> None:
    with open(output_file, 'w') as file:
        for month in data:
            for link in month:
                file.write(link + '\n')
    print(f"Data written to {output_file}")
    
    return None






"""----------------Main function----------------"""

if True:
    required_monthes = last_three_months()
    print(required_monthes)
    links = []
    for cur_url in required_monthes:
        try:
            driver = setup_selenium()
            print("URL", str(URL + cur_url))
            driver.get(str(URL + cur_url))
            isValid = await_of_load()

            if isValid:
                print("Valid succesfull - ", cur_url)
                links.append(extract_data(cur_url))
                
            else:
                print("Error in validation")

            driver.quit()

        except Exception as e:
            print(e)
            
    write_links(output_file, links)
    driver.quit()

