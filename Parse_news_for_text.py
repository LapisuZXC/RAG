import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import re


# Путь файла записи
output_file = "Data/news_links.txt"



def last_three_months():
    today = datetime.now()
    last_months = []

    for i in range(0, 3):
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


# body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > div.newsdsl > div.newstext-con


def extract_data(url: str) -> [str]:

    # Define the selector for all elements with the required classes
    selectors = [
        '.headertext',  # Class for the header text
        '.news-block',  # Class for the news block
        '.featured-quote',  # Class for featured quotes
    ]

    # List to store the extracted text
    text_data = []

    parent_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.index > div.standard-box.standard-list"

    try:
        heading_element = driver.find_element(By.CSS_SELECTOR, "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article > h1")
        text_data.append(heading_element.text)

        for selector in selectors:
            try:
                # Find all matching elements for the current class
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.tag_name != 'img' and element.tag_name != 'video':  # Ensure it's not an image or video
                        text_data.append(element.text)
            except Exception as e:
                print(f"Error extracting from selector '{selector}': {e}")
    except Exception as e:
        print("Error due to extraction:", e)
    # Output the extracted text
    return data


def write_links(output_file: str, data: {str}) -> None:
    with open(output_file, 'w') as file:
        for month in data:
            for link in month:
                file.write(link + '\n')
    print(f"Data written to {output_file}")
    
    return None










def try_extract(driver):

    # Define the selector for all elements with the required classes
    selectors = [
        '.headertext',  # Class for the header text
        '.news-block',  # Class for the news block
        '.featured-quote',  # Class for featured quotes
    ]

    # List to store the extracted text
    text_data = []

    # Loop through the selectors and extract text from each element
    for selector in selectors:
        try:
            # Find all matching elements for the current class
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                cleaned_text = re.sub(r'[^\x00-\x7F]+', '', element.text)
                if cleaned_text:
                    text_data.append(cleaned_text)
        except Exception as e:
            print(f"Error extracting from selector '{selector}': {e}")


    # Now, let's extract the tables
    tables = driver.find_elements(By.CSS_SELECTOR, '.table-container.event-matches-table')
    for idx, table in enumerate(tables, start=1):
        try:
            table_data = []
            headers = table.find_elements(By.TAG_NAME, 'th')
            rows = table.find_elements(By.TAG_NAME, 'tr')

            # Capture header row text
            table_headers = [clean_text(header.text) for header in headers]
            table_data.append({"headers": table_headers})

            # Capture table body rows
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                row_data = []
                for col in columns:
                    cleaned_data = clean_text(col.text)
                    if cleaned_data:
                        row_data.append(cleaned_data)
                if row_data:
                    table_data.append(row_data)

            if table_data:
                text_data.append({
                    "table": f"Table {idx}",
                    "data": table_data
                })

        except Exception as e:
            print(f"Error extracting table data: {e}")



        # Output the extracted text
        for idx, text in enumerate(text_data, start=1):
            print(f"Extracted Text {idx}: {text}")




def try_extract_all_data(driver):
     # Get the content of the article using the specified CSS selector
    article_element = driver.find_element(By.CSS_SELECTOR, 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article')
    
    # Get the page's HTML (after JS has loaded content)
    page_html = article_element.get_attribute('outerHTML')
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_html, 'html.parser')

    # Extract headers (h1, h2, h3, h4, h5, h6)
    headers = [header.get_text(strip=True) for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    
    # Extract strong text (bold)
    strong_text = [strong.get_text(strip=True) for strong in soup.find_all('strong')]
    
    # Extract paragraphs (text inside <p>)
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    
    # Extract quotes (blockquotes)
    blockquotes = [blockquote.get_text(strip=True) for blockquote in soup.find_all('blockquote')]
    
    # Extract all links (anchor tags)
    links = [link.get_text(strip=True) for link in soup.find_all('a')]
    
    # Extract tables (table tags and their contents)
    tables = []
    for table in soup.find_all('table'):
        table_data = []
        for row in table.find_all('tr'):
            row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            table_data.append(row_data)
        tables.append(table_data)

    # Combine all extracted information
    data = {
        'headers': headers,
        'strong_text': strong_text,
        'paragraphs': paragraphs,
        'blockquotes': blockquotes,
        'links': links,
        'tables': tables,
    }
    print(data)
    return data











"""----------------Main function----------------"""

if True:
    #link = 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
    link = 'https://www.hltv.org/news/41221/short-news-week-12'
    data = []
    try:
        driver = setup_selenium()
        print("URL", link)
        driver.get(link)
        isValid = await_of_load()

        if isValid:
            print("Valid succesfull - ", link)
            try_extract_all_data(driver)
            #data.append(extract_data(link))
            
        else:
            print("Error in validation")

        driver.quit()

    except Exception as e:
        print(e)


    #print(data)
    #write_links(output_file, links)
    driver.quit()

