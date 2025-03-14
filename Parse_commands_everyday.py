from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import os
import pandas as pd
from datetime import datetime
from util.setup_selenium import setup_selenium

# URL страницы
URL = "https://www.hltv.org/ranking/teams"
# Путь файла записи
output_file = "Data/team_ranking.csv"


def setup_selenium() -> "driver":
    # Настройка Selenium

    driver_path = "/usr/bin/chromedriver"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(driver_path), options=options)

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
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking",
                )
            )
        )
        print("Таблица загружена.")
        return True

    except Exception as e:
        print(f"Ошибка при загрузке таблицы: {e}")
        return False


def extract_data(url):  # TODO написать функцию для парсинга
    [_, cur_year, cur_month, cur_date] = url.split("/")
    data = {
        "Year": [],
        "Month": [],
        "Date": [],
        "Rank": [],
        "Name_of_team": [],
        "Members": [],
        "Link": [],
    }
    try:
        # Locate all parent elements
        parent_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking > div:nth-child(1) > div",
        )
        # Loop through each parent element
        for index, parent_element in enumerate(parent_elements, start=1):
            if index < 4:
                continue
            try:
                child_element_position = parent_element.find_element(
                    By.CSS_SELECTOR, "div > div.ranking-header > span.position"
                )
                child_element_team_link = parent_element.find_element(
                    By.CSS_SELECTOR, "div > div.lineup-con > div > a:nth-child(1)"
                )
                try:
                    child_element_team_name = parent_element.find_element(
                        By.CSS_SELECTOR,
                        "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers.teamLineExpanded > span.name",
                    )
                except:
                    child_element_team_name = parent_element.find_element(
                        By.CSS_SELECTOR,
                        "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers > span.name",
                    )

                position = child_element_position.text
                team_name = child_element_team_name.text
                link_team = child_element_team_link.get_attribute("href")

                elements_players = parent_element.find_elements(
                    By.CSS_SELECTOR, "div > div.lineup-con > table > tbody > tr > td"
                )
                # Count the number of players
                count_of_players = len(elements_players)
                player_links = []
                player_names = []
                for i in range(count_of_players):
                    try:
                        cur_player = parent_element.find_element(
                            By.CSS_SELECTOR,
                            f"div > div.lineup-con > table > tbody > tr > td:nth-child({
                                i + 1
                            }) > a",
                        )
                    except:
                        cur_player = parent_element.find_element(
                            By.CSS_SELECTOR,
                            f"div > div.lineup-con.hidden > table > tbody > tr > td:nth-child({
                                i + 1
                            }) > a",
                        )
                    player_links.append(cur_player.get_attribute("href"))
                    cur_player = cur_player.find_element(
                        By.CSS_SELECTOR, "img")
                    player_names.append(cur_player.get_attribute("alt"))

                player_dict = {}
                for i, (link, name) in enumerate(
                    zip(player_links, player_names), start=1
                ):
                    key1 = f"Name_player{i}"
                    player_dict[key1] = name
                    key2 = f"Link_player{i}"
                    player_dict[key2] = link

                data_one = {
                    "Year": cur_year,
                    "Month": cur_month,
                    "Date": cur_date,
                    "Rank": position,
                    "Name_of_team": team_name,
                    "Members": player_dict,
                    "Link": link_team,
                }

                # print(f"  {position=}")
                # print(f"  {team_name=}")
                # print(f"  {link_team=}")
                # print(f"  {count_of_players=}")
                # print(player_links)
                # print(player_names)

                for key in data.keys():
                    if key in data_one:
                        data[key].append(data_one[key])
                    else:
                        data[key].append(None)

            except Exception as e:
                print(e)

    except Exception as e:
        print(f"Ошибка при извлечении ссылки по селектору {'selector'}: {e}")

    return data


def write_links(output_file, data):
    if not os.path.exists(output_file):
        imp_data = {
            "Year": [],
            "Month": [],
            "Date": [],
            "Rank": [],
            "Name_of_team": [],
            "Members": [],
            "Link": [],
        }
        data_frame = pd.DataFrame(imp_data)
        data_frame.to_csv(output_file, index=False)
    data_frame = pd.DataFrame(data)
    data_frame.to_csv(output_file, mode="a", index=False, header=False)
    print(f"Data written to {output_file}")


"""----------------Main function----------------"""

if __name__ == "__main__":
    cur_year = datetime.today().strftime("%Y")
    cur_month = int(datetime.today().strftime("%m"))
    cur_date = datetime.today().strftime("%d")
    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    # cur_year = input()
    # cur_month = int(input())
    # cur_date = input()

    cur_url = f"/{cur_year}/{months[cur_month - 1]}/{cur_date}"
    print(cur_url)
    try:
        driver = setup_selenium()
        driver.get(str(URL + cur_url))
        await_of_load()
        isValid = await_of_load()

        if isValid:
            print("Today is a perfect day")
            cur_data = extract_data(cur_url)
            write_links(output_file, cur_data)

        driver.quit()

    except Exception as e:
        print(e)

    driver.quit()
