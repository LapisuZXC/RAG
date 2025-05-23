from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from fake_useragent import UserAgent

import undetected_chromedriver as uc


def setup_selenium():
    options = uc.ChromeOptions()

    # Фиксированный User-Agent (лучше использовать реальный)
    user_agent = UserAgent().random
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Убираем автоматическое управление браузером
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Запуск браузера

    options.binary_location = "/usr/bin/chromium"  # закоментить для локалки
    driver = uc.Chrome(options=options, headless=True, version_main=135)

    # Убираем следы Selenium с помощью stealth
    stealth(
        driver,
        user_agent=user_agent,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver
