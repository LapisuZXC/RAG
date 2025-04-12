from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
from util.setup_selenium import setup_selenium
import random
from datetime import datetime, timedelta

URL = "https://www.hltv.org/ranking/teams"
OUTPUT_FILE = "data/processed/team_ranking.csv"


"""

Старая версия parse_teams_all.py 
Хз надо ли сносить

"""




def await_load(driver):
    try:
        WebDriverWait(driver, random.randint(5, 10)).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ranking"))
        )
        return True
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return False


def generate_urls(start_date, end_date):
    urls = []
    current_date = start_date
    while current_date <= end_date:
        url = f"/{current_date.year}/{current_date.strftime('%B').lower()}/{
            current_date.day
        }"
        urls.append(url)
        current_date += timedelta(days=7)  # Шаг в 7 дней
    return urls


def extract_data(driver, url):
    _, year, month, day = url.split("/")
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
        parent_elements = driver.find_elements(
            By.CSS_SELECTOR, "div.ranking > div:nth-child(1) > div"
        )[3:]
        for index, parent in enumerate(parent_elements, start=1):
            try:
                position = parent.find_element(By.CSS_SELECTOR, "span.position").text
                team_name = parent.find_element(
                    By.CSS_SELECTOR, "div.teamLine span.name"
                ).text

                if index == 1:
                    link_team_selector = "div > div.lineup-con > div > a:nth-child(1)"
                else:
                    link_team_selector = (
                        "div > div.lineup-con.hidden > div > a:nth-child(1)"
                    )

                link_team = parent.find_element(
                    By.CSS_SELECTOR, link_team_selector
                ).get_attribute("href")

                players = parent.find_elements(
                    By.CSS_SELECTOR, "div.lineup-con table tbody tr td a"
                )
                player_dict = {}
                for i, p in enumerate(players):
                    try:
                        player_dict[f"Name_player{i + 1}"] = p.find_element(
                            By.TAG_NAME, "img"
                        ).get_attribute("alt")
                        player_dict[f"Link_player{i + 1}"] = p.get_attribute("href")
                    except Exception as e:
                        print(f"Ошибка при парсинге игрока {i + 1}: {e}")
                        continue

                data["Year"].append(year)
                data["Month"].append(month)
                data["Date"].append(day)
                data["Rank"].append(position)
                data["Name_of_team"].append(team_name)
                data["Members"].append(player_dict)
                data["Link"].append(link_team)
            except Exception as e:
                print(f"Ошибка при обработке команды: {e}")
                continue
    except Exception as e:
        print(f"Ошибка при получении списка команд: {e}")
    return data


def write_data(output_file, data):
    try:
        df = pd.DataFrame(data)
        df.to_csv(output_file, mode="w", index=False, header=True)
        print(f"Data written to {output_file}")
    except Exception as e:
        print(f"Ошибка при записи данных в файл: {e}")


if __name__ == "__main__":
    start_date = datetime(2023, 1, 2)  # 2 января 2023
    end_date = datetime(2024, 12, 31)  # До конца 2024 года
    urls = generate_urls(start_date, end_date)
    driver = setup_selenium()

    all_data = {
        "Year": [],
        "Month": [],
        "Date": [],
        "Rank": [],
        "Name_of_team": [],
        "Members": [],
        "Link": [],
    }

    for cur_url in urls:
        try:
            print(f"Парсинг данных за {cur_url}")
            driver.get(URL + cur_url)
            if await_load(driver):
                try:
                    data = extract_data(driver, cur_url)
                    for key in all_data:
                        all_data[key].extend(data[key])
                except Exception as e:
                    print(f"Ошибка при обработке данных из {cur_url}: {e}")
        except Exception as e:
            print(f"Ошибка при загрузке страницы {cur_url}: {e}")

    write_data(OUTPUT_FILE, all_data)
    driver.quit()
