import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from util.setup_selenium import setup_selenium
from typing import Dict, List, Union

class driver_context_manager(object):
    """
    Используем контекстный менеджер для гарантированного выхода из драйвера даже при возникновении ошибки.
    """
    def __enter__(self):
        self.driver = setup_selenium()
        print("setup driver")
        return self
    
    def __exit__(self, typeExeption, value, traceback):
        self.driver.quit()
        print("quited driver")
        if typeExeption is not None:
            print("An exception in driver_context_manager")
            print(f"{typeExeption=}")
            print(f"{value=}")
            print(f"{traceback=}")
        return self


def await_of_load(driver: webdriver) -> bool:
    """
    Эта функция заставляет программу ожидать 5 секунд, пока страница не прогрузится, чтобы мы могли собрать все данные
    """
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.ranking")))
        print("Таблица загружена.")
        return True
    
    except Exception as e:
        print(f"Ошибка при загрузке таблицы: {e}")

    return False


def write_links(output_file: str, data: list[str], data_csv_format: Dict[str, Union[str, int, List[str]]]) -> None:
    if not os.path.exists(output_file):
        data_frame = pd.DataFrame(data_csv_format)
        data_frame.to_csv(output_file, index=False)

    data_frame = pd.DataFrame(data)
    data_frame.to_csv(output_file, mode="a", index=False, header=False)

    print(f"Data written to {output_file}")
    return None