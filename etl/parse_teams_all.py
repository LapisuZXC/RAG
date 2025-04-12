from selenium import webdriver
from selenium.webdriver.common.by import By
from util.datetime_util import generate_date_list_every_week
from datetime import datetime
from typing import Dict, List, Union
from util.selenium_workflow import driver_context_manager, await_of_load
from util.csv_workflow import write_links

URL = 'https://www.hltv.org/ranking/teams'
output_file = "data/processed/team_ranking.csv"

data_csv_format = {
            "Year": [],
            "Month": [],
            "Date": [],
            "Rank": [],
            "Name_of_team": [],
            "Members": [],
            "Link": []
    }


TABLE_SELECTOR = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking"
# Селектор общей таблицы данных

def extract_data(url: str, driver: webdriver) -> Dict[str, Union[str, int, List[Dict[str, str]]]]:
    _, cur_year, cur_month, cur_date = url.split('/')
    data = data_csv_format
    try:
        parent_elements = driver.find_elements(By.CSS_SELECTOR, "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking > div:nth-child(1) > div")
        # Заходим в элмент таблицы через селектор
        for index, parent_element in enumerate(parent_elements, start=1):
            # Пройдем по всем элементам таблицы, где 1 элемент - 1 команда
            if index < 4:
                continue
            try:
                #-----------------парсим команды-----------------------
                child_element_position = parent_element.find_element(By.CSS_SELECTOR, "div > div.ranking-header > span.position")
                child_element_team_link = parent_element.find_element(By.CSS_SELECTOR, "div > div.lineup-con > div > a:nth-child(1)")
                try:
                    child_element_team_name = parent_element.find_element(By.CSS_SELECTOR, "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers.teamLineExpanded > span.name")
                except:
                    child_element_team_name = parent_element.find_element(By.CSS_SELECTOR, "div > div.ranking-header > div.relative > div.teamLine.sectionTeamPlayers > span.name")
                
                position = child_element_position.text
                team_name = child_element_team_name.text
                link_team = child_element_team_link.get_attribute("href")
                
                #-----------------парсим игроков-----------------------
                elements_players = parent_element.find_elements(By.CSS_SELECTOR, "div > div.lineup-con > table > tbody > tr > td")
                count_of_players = len(elements_players)
                player_links, player_names = list(), list()

                for i in range(count_of_players):
                    try:
                        cur_player = parent_element.find_element(By.CSS_SELECTOR, f"div > div.lineup-con > table > tbody > tr > td:nth-child({i+1}) > a")
                    except:
                        cur_player = parent_element.find_element(By.CSS_SELECTOR, f"div > div.lineup-con.hidden > table > tbody > tr > td:nth-child({i+1}) > a")
                    player_links.append(cur_player.get_attribute("href"))
                    cur_player = cur_player.find_element(By.CSS_SELECTOR, "img")
                    player_names.append(cur_player.get_attribute("alt"))
                
                #-----------------сохраняем данные-----------------------
                player_dict = dict()
                for i, (link, name) in enumerate(zip(player_links, player_names), start=1):
                    key1 = f"Name_player_{i}"
                    player_dict[key1] = name
                    key2 = f"Link_player_{i}"
                    player_dict[key2] = link
                
                data["Year"].append(cur_year)
                data["Month"].append(cur_month)
                data["Date"].append(cur_date)
                data["Rank"].append(position)
                data["Name_of_team"].append(team_name)
                data["Members"].append(player_dict)
                data["Link"].append(link_team)

            except Exception as e:
                print(e)

    except Exception as e:
        print(f"Ошибка при извлечении ссылки по селектору selector: {e}")

    return data





def main():
    start_date = datetime(2023, 1, 2)  # 2 января 2023
    end_date = datetime(2024, 12, 31)  # До конца 2024 года
    urls = generate_date_list_every_week(start_date, end_date)

    for cur_url in urls:
        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            
            print("Getting data from: ", str(URL + cur_url))
            driver.get(str(URL + cur_url))

            isValid = await_of_load(driver, TABLE_SELECTOR)
            if isValid:
                print("Found data")
                cur_data = extract_data(cur_url, driver)
                write_links(output_file, cur_data, data_csv_format)
            else:
                print("Cant find data")


if __name__ == "__main__":
    main()