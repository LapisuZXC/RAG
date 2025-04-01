from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from util.setup_selenium import setup_selenium

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


def await_of_load(driver: webdriver, selector: str) -> bool:
    """
    Эта функция заставляет программу ожидать 5 секунд, пока страница не прогрузится, чтобы мы могли собрать все данные
    """
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        print("Таблица загружена.")
        return True
    
    except Exception as e:
        print(f"Ошибка при загрузке таблицы: {e}")

    return False
