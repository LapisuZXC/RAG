from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
import pandas as pd


def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Запуск без интерфейса
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service("chromedriver")  # Убедись, что chromedriver в PATH
    driver = webdriver.Chrome(service=service, options=options)

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver


def parse_team_matches(team_id, team_name, driver):
    url = f"https://www.hltv.org/stats/teams/matches/{team_id}/{team_name}"
    driver.get(url)
    time.sleep(3)  # Ожидание загрузки страницы

    matches = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    current_event = None
    for row in rows:
        classes = row.get_attribute("class").split()

        if "first" in classes:
            cells = row.find_elements(By.TAG_NAME, "td")
            date = cells[0].text.strip()
            event = cells[1].text.strip()
            opponent = cells[3].text.strip()
            map_played = cells[4].text.strip()
            result = cells[5].text.strip()
            win_loss = cells[6].text.strip()
            current_event = event  # Запоминаем турнир
        else:
            cells = row.find_elements(By.TAG_NAME, "td")
            opponent = cells[2].text.strip()
            map_played = cells[3].text.strip()
            result = cells[4].text.strip()
            win_loss = cells[5].text.strip()

        matches.append(
            [team_name, date, current_event, opponent, map_played, result, win_loss]
        )

    return matches


def main():
    df_teams = pd.read_csv("Data/unique_teams.csv")  # Загружаем команды
    driver = setup_driver()

    all_matches = []

    for _, row in df_teams.iterrows():
        team_id = row["team_id"]
        team_name = row["team_name"].replace(" ", "-").lower()
        print(f"Парсим {team_name}...")

        try:
            matches = parse_team_matches(team_id, team_name, driver)
            all_matches.extend(matches)
        except Exception as e:
            print(f"Ошибка при парсинге {team_name}: {e}")

    driver.quit()

    df_matches = pd.DataFrame(
        all_matches,
        columns=["team_name", "date", "event",
                 "opponent", "map", "result", "win_loss"],
    )
    df_matches.to_csv("Data/matches.csv", index=False)
    print("Файл matches.csv успешно сохранён!")


if __name__ == "__main__":
    main()
