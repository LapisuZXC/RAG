from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import os
import pandas as pd

# URL страницы
URL = 'https://www.hltv.org/ranking/teams'
# Путь файла записи
output_file = "Data/team_ranking.csv"


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




def await_of_load() -> None:
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.stats-table")))
        print("Таблица загружена.")
    except Exception as e:
        print(f"Ошибка при загрузке таблицы: {e}")
        driver.quit()
        exit()


def parse_ranking_due_date(year_from: int, year_to: int) -> [str]:
    urls = []
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    for cur_year in range(year_from, year_to+1):
        for month in months:
            for date in range(1, 32):
                urls.append(f"/{cur_year}/{month}/{date}")

    return urls


def extract_data(url: str) -> [str]:  # TODO написать функцию для парсинга
    [_, cur_year, cur_month, cur_date] = url.split('/')
    # data = {
    #         "Year": [cur_year for i in range(50)],
    #         "Month": [cur_month for i in range(50)],
    #         "Date": [cur_date for i in range(50)],
    #         "Rank": [],
    #         "Name_of_team": [],
    #         "Members": [],
    #         "Link": []
    #     }
    
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        object = element.get_attribute('href')
        if object:
            data.append(object)
            # print(f"Найден объект: {object}")
        else:
            print(f"Ссылка не найдена в элементе по селектору: {selector}")
    except Exception as e:
        print(f"Ошибка при извлечении ссылки по селектору {selector}: {e}")

    return data


def write_links(output_file: str, data: {str}) -> None:
    if not os.path.exists(output_file):
        imp_data = {
            "Year": [],
            "Month": [],
            "Date": [],
            "Rank": [],
            "Name_of_team": [],
            "Members": [],
            "Link": []
        }
        data_frame = pd.DataFrame(imp_data)
        data_frame.to_csv(output_file, index=False)
    data_frame = pd.DataFrame(data)
    data_frame.to_csv(output_file, mode="a", index=False, header=False)
    print(f"Data written to {output_file}")






"""----------------Main function----------------"""

"""cr_data = {
            "Year": ['2023', '2023'],
            "Month": ['November', 'December'],
            "Date": ['1', '2'],
            "Rank": ['1', '1'],
            "Name_of_team": ['abs', 'abs'],
            "Members": [{"player1": "https://example.com/player1", "player2": "https://example.com/player2"},
        {"player3": "https://example.com/player3", "player4": "https://example.com/player4"}],
            "Link": [ "https://example.com/team1",
                    "https://example.com/team2",]
        }
        
"""
#write_links(output_file, cr_data)

#df = pd.read_csv(output_file)   

# Display all data
#print(df)

if True:

    urls = parse_ranking_due_date(2023, 2024)

    for cur_url in urls[:7]:
        try:
            driver.get(URL + cur_url)
            await_of_load()

            cur_data = extract_data(cur_url)

            # Закрытие драйвера
            driver.quit()
            
            # Сохранение ссылок в файл
            write_links(output_file, cur_data)

        finally:
            pass


