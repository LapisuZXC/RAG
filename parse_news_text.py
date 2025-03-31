from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import re
from util.setup_selenium import setup_selenium
from util.selenium_workflow import await_of_load

# Путь файла записи
output_file = "Data/raw/last_news_links.txt"




def try_extract_all_data(driver) -> dict:
     # Get the content of the article using the specified CSS selector
    article_element = driver.find_element(By.CSS_SELECTOR, 'body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > article')
    
    # Get the page's HTML (after JS has loaded content)
    page_html = article_element.get_attribute('outerHTML')
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_html, 'html.parser')

    # Extract headers (h1, h2, h3, h4, h5, h6)
    headers = [re.sub(r'[^\x00-\x7F]+', '', header.get_text(strip=True)) for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    
    # Extract strong text (bold)
    strong_text = [re.sub(r'[^\x00-\x7F]+', '', strong.get_text(strip=True)) for strong in soup.find_all('strong')]
    
    # Extract paragraphs (text inside <p>)
    paragraphs = [re.sub(r'[^\x00-\x7F]+', '', p.get_text(strip=True)) for p in soup.find_all('p')]
    
    # Extract quotes (blockquotes)
    blockquotes = [blockquote.get_text(strip=True) for blockquote in soup.find_all('blockquote')]
    
    featured_quotes = []

    elements = driver.find_elements(By.CSS_SELECTOR, '.featured-quote')
    for element in elements:
        cleaned_text = re.sub(r'[^\x00-\x7F]+', '', element.text)
        if cleaned_text:
            featured_quotes.append(cleaned_text)

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
        'featured_quotes': featured_quotes,
        'blockquotes': blockquotes,
        'tables': tables,
    }

    for key, value in data.items():
        print(f"{key}:")
        if isinstance(value, list):
            for item in value:
                print(f"    - {item}")
        else:
            print(f"    {value}")
        print()  # Add an empty line for better readability

    return data





"""---------------------------Вариант 2, нет таблиц, но текст более структурирован-------------------------------------"""

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







"""----------------Main function----------------"""

if True:
    #link = 'https://www.hltv.org/news/40889/twistzz-it-does-suck-not-being-able-to-play-cluj'
    link = 'https://www.hltv.org/news/41221/short-news-week-12'
    try:
        driver = setup_selenium()
        print("URL", link)
        driver.get(link)
        isValid = await_of_load()

        if isValid:
            print("Valid succesfull - ", link)
            data = try_extract_all_data(driver)
            #data.append(extract_data(link))
            
        else:
            print("Error in validation")

        driver.quit()

    except Exception as e:
        print(e)


    #print(data)
    driver.quit()

