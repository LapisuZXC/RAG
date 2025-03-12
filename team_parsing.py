import json
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium import webdriver
from util.datetime_util import get_date_range

chromium_binary_path = "/usr/bin/chromium"
chromedriver_path = "/usr/bin/chromedriver"

service = Service(chromedriver_path)

options = webdriver.ChromeOptions()
options.binary_location = chromium_binary_path
options.add_argument("--headless")  # Запуск без UI
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=service, options=options)

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Linux",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)
base_url = "https://www.hltv.org/stats/teams"

time_filter = get_date_range()
rankign_filter = "rankingFilter=Top50"


top_50_url = base_url + "?" + time_filter + "&" + rankign_filter


driver.get(top_50_url)


def get_top_50_teams():
    try:
        # Ожидание загрузки таблицы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".stats-table"))
        )

        # Извлекаем заголовки столбцов
        headers = [
            th.text.strip()
            for th in driver.find_elements(By.CSS_SELECTOR, "thead th")
            if th.text.strip()
        ]

        # Добавляем новый заголовок для ID команды
        headers.insert(1, "id")

        # Ищем все строки с данными (пропускаем заголовок)
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

        teams_data = []

        for i, row in enumerate(rows):
            if i > 49:
                break
            try:
                # Ищем ячейки
                cells = row.find_elements(By.CSS_SELECTOR, "td")

                # Извлекаем ссылку команды
                team_link_element = row.find_element(
                    By.CSS_SELECTOR, "td.teamCol-teams-overview a"
                )
                team_href = (
                    team_link_element.get_attribute("href")
                    if team_link_element
                    else None
                )

                # Проверяем, есть ли у элемента ссылка
                if team_href is None:
                    print(f"⚠️ Предупреждение: Ссылка не найдена в строке {i + 1}")
                    team_id = "unknown"
                else:
                    # Ищем ID с помощью регулярного выражения
                    re_match = re.search(r"/teams/(\d+)/", team_href)
                    team_id = re_match.group(1) if re_match else "unknown"

                # Вставляем ID в начало списка данных
                team_data = (
                    [cells[0].text.strip()]
                    + [team_id]
                    + [cell.text.strip() for cell in cells[1:]]
                )

                # Создаём словарь
                team_info = {headers[j]: team_data[j] for j in range(len(headers))}
                teams_data.append(team_info)

            except Exception as e:
                print(f"❌ Ошибка в строке {i + 1}: {e}")

        return teams_data

    except Exception as e:
        print("Ошибка:", e)
        return []


# Получаем данные о командах
teams_list = get_top_50_teams()

# Сохраняем в JSON
with open("teams.json", "w", encoding="utf-8") as f:
    json.dump(teams_list, f, ensure_ascii=False, indent=4)

print("Данные успешно сохранены в teams.json")

# Закрываем браузер
driver.quit()
