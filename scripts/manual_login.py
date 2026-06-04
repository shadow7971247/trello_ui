"""Один раз войти в Trello вручную — сессия сохранится в .chrome-profile."""

from __future__ import annotations

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config

if __name__ == "__main__":
    config.validate()
    options = Options()
    profile = config.chrome_user_data_dir or ".chrome-profile"
    options.add_argument(f"--user-data-dir={profile}")
    options.add_argument("--window-size=1400,900")
    driver = webdriver.Chrome(options=options)
    driver.get("https://trello.com/login")
    print("Войдите в Trello в открывшемся окне. Закройте браузер после входа.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    driver.quit()
