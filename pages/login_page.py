"""Страница входа Trello / Atlassian."""

from __future__ import annotations

import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selene import browser

ATLASSIAN_LOGIN = (
    "https://id.atlassian.com/login"
    "?continue=https://trello.com"
    "&application=trello"
)

# Atlassian: id вида username-uid1 — стабильнее data-testid / name
EMAIL_FIELD = (
    'input[data-testid="username"], '
    'input[name="username"], '
    'input[id^="username-"], '
    'input[type="email"][autocomplete="username"]'
)
PASSWORD_FIELD = (
    'input[data-testid="password"], '
    'input[name="password"], '
    'input[id^="password-"], '
    'input[type="password"]'
)
SUBMIT_BUTTON = (
    '#login-submit, '
    'button[data-testid="login-submit"], '
    'button[type="submit"], '
    '#login-button'
)


class LoginPage:
    def __init__(self, timeout: float = 30) -> None:
        self._timeout = timeout

    @property
    def _driver(self):
        return browser.driver

    @property
    def _wait(self) -> WebDriverWait:
        return WebDriverWait(self._driver, self._timeout)

    def open(self) -> LoginPage:
        with allure.step("Открыть Trello"):
            browser.open("/")
            time.sleep(2)
        return self

    def login(self, email: str, password: str) -> LoginPage:
        with allure.step(f"Войти под пользователем {email}"):
            if self._is_logged_in():
                return self
            self._driver.get(ATLASSIAN_LOGIN)
            self._enter_email(email)
            self._enter_password(password)
            self._wait.until(lambda d: "trello.com" in d.current_url)
            time.sleep(2)
            self._wait.until(lambda _: self._is_logged_in())
        return self

    def _is_logged_in(self) -> bool:
        if self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="account-menu"]'):
            return True
        url = self._driver.current_url
        if "id.atlassian.com" in url or "/login" in url:
            return False
        if "trello.com" not in url:
            return False
        if "/u/" in url or "/boards" in url:
            return True
        return bool(
            self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="board-name"]')
        )

    def _enter_email(self, email: str) -> None:
        field = self._wait.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, EMAIL_FIELD))
        )
        field.clear()
        field.send_keys(email)
        self._click_submit()

    def _enter_password(self, password: str) -> None:
        field = self._wait.until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, PASSWORD_FIELD))
        )
        field.clear()
        field.send_keys(password)
        self._click_submit()

    def _click_submit(self) -> None:
        button = self._wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, SUBMIT_BUTTON))
        )
        button.click()
