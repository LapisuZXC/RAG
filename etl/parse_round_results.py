import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.setup_selenium import setup_selenium


def parse_round_results(match_link, driver):
    """Парсит результаты раундов по указанной ссылке."""
    driver.get(match_link)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.round-history-team-row"))
    )
    rounds = driver.find_elements(
        By.CSS_SELECTOR, "div.round-history-team-row:nth-child(1) > img"
    )
    round_1 = rounds[3]
    round_13 = rounds[15]

    # print(round_1.get_attribute("src"))

    def is_round_win(round_element):
        return (
            round_element.get_attribute("src")
            != "https://www.hltv.org/img/static/scoreboard/emptyHistory.svg"
        )

    round_1_win = is_round_win(round_1)
    round_13_win = is_round_win(round_13)
    return round_1_win, round_13_win


def main():
    df_matches = pd.read_csv("../data/processed/matches.csv")
    driver = setup_selenium()

    round_results = []

    for _, row in df_matches.iterrows():
        match_link = row["match_link"]
        try:
            round_1_win, round_13_win = parse_round_results(match_link, driver)
            round_results.append((round_1_win, round_13_win))
        except Exception as e:
            print(f"Ошибка при парсинге {match_link}: {e}")
            round_results.append((None, None))

    driver.quit()

    df_matches["round_1_win"], df_matches["round_15_win"] = zip(*round_results)
    df_matches.to_csv("../data/processed/matches.csv", index=False)
    print("Файл data/matches.csv успешно обновлён!")


if __name__ == "__main__":
    main()
