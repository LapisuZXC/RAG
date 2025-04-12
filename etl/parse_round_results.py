import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.setup_selenium import setup_selenium

#TODO Не работает
"""


Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\etl\parse_round_results.py", line 58, in <module>
    main()
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\etl\parse_round_results.py", line 52, in main
    df_matches["round_1_win"], df_matches["round_15_win"] = zip(*round_results)
    ~~~~~~~~~~^^^^^^^^^^^^^^^
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\venv\Lib\site-packages\pandas\core\frame.py", line 4311, in __setitem__
    self._set_item(key, value)
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\venv\Lib\site-packages\pandas\core\frame.py", line 4524, in _set_item
    value, refs = self._sanitize_column(value)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\venv\Lib\site-packages\pandas\core\frame.py", line 5266, in _sanitize_column
    com.require_length_match(value, self.index)
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\venv\Lib\site-packages\pandas\core\common.py", line 573, in require_length_match
    raise ValueError(
ValueError: Length of values (1) does not match length of index (365)
Exception ignored in: <function Chrome.__del__ at 0x000002CAB4991BC0>
Traceback (most recent call last):
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\venv\Lib\site-packages\undetected_chromedriver\__init__.py", line 843, in __del__
  File "E:\My_projects\Uncompleted_projects\Proect_practikim_llm\RAG\venv\Lib\site-packages\undetected_chromedriver\__init__.py", line 798, in quit





"""

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
    df_matches = pd.read_csv("data/processed/matches.csv")
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
        break
    driver.quit()

    df_matches["round_1_win"], df_matches["round_15_win"] = zip(*round_results)
    df_matches.to_csv("data/processed/matches.csv", index=False)
    print("Файл matches.csv успешно обновлён!")


if __name__ == "__main__":
    main()
