import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
import os
# Список User-Agent для ротации
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
]


def setup_selenium():
    is_will_install_driver = False
    if os.path.exists("/usr/bin/chromedriver"):
        driver_path = "/usr/bin/chromedriver"
    elif os.path.exists("F:/DriverManager/chromedriver-win64/chromedriver.exe"):
        driver_path = "F:/DriverManager/chromedriver-win64/chromedriver.exe"
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()

    options = webdriver.ChromeOptions()

    # Выбираем случайный User-Agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")

    # Настройки Chrome
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Добавляем прокси, если указано

    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    # Настраиваем Selenium Stealth с тем же User-Agent
    stealth(
        driver,
        user_agent=user_agent,  # Теперь User-Agent совпадает
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver



