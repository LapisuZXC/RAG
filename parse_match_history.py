import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.datetime_util import get_date_range
from util.setup_selenium import setup_selenium

TIME_FILTER = get_date_range(time_filter="2023-2024")


def parse_team_matches(team_id, team_name, driver):
    # G2,5995
    # https://www.hltv.org/stats/teams/matches/5995/G2
    url = (
        f"https://www.hltv.org/stats/teams/matches/{team_id}/{team_name}"
        + "?"
        + TIME_FILTER
    )
    driver.get(url)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
    )  # Ожидание загрузки данных

    matches = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    current_event = None
    for i, row in enumerate(rows):
        # !!!!
        cells = row.find_elements(By.TAG_NAME, "td")
        date = cells[0].text.strip()
        link_elements = row.find_elements(
            By.CSS_SELECTOR, "td:nth-child(1) > a")
        link = link_elements[0].get_attribute(
            "href") if link_elements else None
        event = cells[1].text.strip()
        opponent = cells[3].text.strip()
        map_played = cells[4].text.strip()
        result = cells[5].text.strip()
        win_loss = cells[6].text.strip()
        current_event = event  # Запоминаем турнир

        matches.append(
            [
                team_name,
                date,
                current_event,
                opponent,
                map_played,
                result,
                win_loss,
                link,
            ]
        )

    return matches


def main():
    df_teams = pd.read_csv("Data/team_test.csv")  # Заменить на unique_teams.csv
    driver = setup_selenium()

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
        columns=[
            "team_name",
            "date",
            "event",
            "opponent",
            "map",
            "result",
            "win_loss",
            "match_link",
        ],
    )

    # Убираем лишние символы из team_name
    df_matches["team_name"] = df_matches["team_name"].apply(
        lambda x: x.strip("[]'"))

    df_matches.to_csv("Data/matches.csv", index=False)
    print("Файл matches.csv успешно сохранён!")


if __name__ == "__main__":
    main()
