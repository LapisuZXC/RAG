from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import os


# URL страницы
url_test = 'https://www.hltv.org/stats/players?startDate=2025-02-08&endDate=2025-03-08&maps=de_dust2&rankingFilter=Top5'
url = 'https://www.hltv.org/stats/players'
# Путь файла записи
output_file = "Data/links.txt"
# Количество ссылок для парсинга
amount_of_players = 203


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


def extract_links(amount_to_parse: int) -> [str]:
    links = []
    for i in range(amount_to_parse):
        selector = f"table.stats-table tr:nth-child({i+1}) td:nth-child(1) a"
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            link = element.get_attribute('href')
            if link:  # Проверяем, что ссылка не пустая
                links.append(link)
                # print(f"Найдена ссылка: {link}")
            else:
                print(f"Ссылка не найдена в элементе по селектору: {selector}")
        except Exception as e:
            print(f"Ошибка при извлечении ссылки по селектору {selector}: {e}")

    return links


def write_links(output_file: str, links: [str]) -> None:
    counter_links = 0
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            existing_links = set(file.read().splitlines())

        with open(output_file, "a", encoding="utf-8") as file:
            for link in links:
                if link not in existing_links:
                    file.write(link + "\n")
                    counter_links+=1

        print(f"Ссылки сохранены в файл: {output_file}")
        print(f"Сохранено {counter_links} новых ссылок")





"""----------------Main function----------------"""

if True:

    # Переход на страницу
    driver.get(url)

    # Ожидание загрузки таблицы
    await_of_load()

    # Извлечение ссылок
    links = extract_links(amount_of_players)

    # Закрытие драйвера
    driver.quit()

    # Сохранение ссылок в файл
    write_links(output_file, links)

