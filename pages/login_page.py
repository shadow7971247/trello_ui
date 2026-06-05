"""Страница входа Trello / Atlassian."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selene import browser

from utils.verification_mail import fetch_verification_code, imap_configured

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
PASSWORD_LOGIN_LINK = (
    'button[data-testid="password-login-button"], '
    '#use-password, '
    'a[data-testid="password-login-button"]'
)
LOGIN_ERROR = (
    '[data-testid="login-error"], '
    '#login-error, '
    '[role="alert"]'
)
COOKIE_ACCEPT = (
    'button[data-testid="cookie-consent-accept"], '
    '#onetrust-accept-btn-handler, '
    'button[id*="accept"]'
)
VERIFICATION_FIELD = (
    'input[data-testid="otp-input"], '
    'input[name="otp"], '
    'input[autocomplete="one-time-code"], '
    'input[id*="otp"], '
    'input[inputmode="numeric"], '
    'input[type="tel"]'
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
            self._open_password_step_if_needed()
            code_request_time = datetime.now(timezone.utc)
            self._enter_password(password)
            self._raise_if_login_error()
            try:
                self._wait.until(
                    lambda d: "trello.com" in d.current_url
                    or self._is_logged_in()
                    or self._has_login_error()
                    or self._needs_verification_code()
                )
            except Exception:
                self._attach_debug("after-password-submit")
                raise
            self._raise_if_login_error()
            self._complete_verification_if_needed(code_request_time)
            self._dismiss_cookie_banner()
            time.sleep(3)
            try:
                self._wait.until(lambda _: self._is_logged_in())
            except Exception:
                self._attach_debug("login-not-detected")
                raise
        return self

    def _is_logged_in(self) -> bool:
        if self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="account-menu"]'):
            return True
        url = self._driver.current_url.lower()
        if "id.atlassian.com" in url:
            return False
        if "trello.com/login" in url or url.rstrip("/").endswith("trello.com/login"):
            return False
        if "trello.com" not in url:
            return False
        if "/u/" in url or "/boards" in url or "/w/" in url:
            return True
        if self._driver.find_elements(By.CSS_SELECTOR, 'a[href*="/login"]'):
            return False
        return bool(
            self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="board-name"]')
            or self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="header-create-menu"]')
            or self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="workspace-boards"]')
            or self._driver.find_elements(By.CSS_SELECTOR, '[data-testid="templates-page"]')
        )

    def _open_password_step_if_needed(self) -> None:
        """Atlassian иногда показывает SSO — нужна ссылка «войти с паролем»."""
        links = self._driver.find_elements(By.CSS_SELECTOR, PASSWORD_LOGIN_LINK)
        if links:
            links[0].click()
            time.sleep(1)

    def _has_login_error(self) -> bool:
        for el in self._driver.find_elements(By.CSS_SELECTOR, LOGIN_ERROR):
            if (el.text or "").strip():
                return True
        return False

    def _raise_if_login_error(self) -> None:
        for el in self._driver.find_elements(By.CSS_SELECTOR, LOGIN_ERROR):
            text = (el.text or "").strip()
            if text:
                self._attach_debug("login-error")
                raise RuntimeError(f"Atlassian login error: {text}")

    def _needs_verification_code(self) -> bool:
        if self._driver.find_elements(By.CSS_SELECTOR, VERIFICATION_FIELD):
            return True
        page = (self._driver.page_source or "").lower()
        return any(
            phrase in page
            for phrase in (
                "verification code",
                "check your email",
                "enter your verification",
                "we sent a code",
                "код подтверждения",
            )
        )

    def _complete_verification_if_needed(self, not_before: datetime) -> None:
        if not self._needs_verification_code():
            return
        if not imap_configured():
            self._attach_debug("verification-no-imap")
            raise RuntimeError(
                "Atlassian запросил код из почты. Настройте IMAP: "
                "TRELLO_IMAP_HOST, TRELLO_IMAP_PASSWORD "
                "(и при необходимости TRELLO_IMAP_USER)."
            )
        with allure.step("Ввести код верификации из почты"):
            code = fetch_verification_code(not_before=not_before)
            self._enter_verification_code(code)
            time.sleep(2)

    def _enter_verification_code(self, code: str) -> None:
        fields = self._driver.find_elements(By.CSS_SELECTOR, VERIFICATION_FIELD)
        visible = [f for f in fields if f.is_displayed()]
        if not visible:
            self._attach_debug("verification-no-field")
            raise RuntimeError("Поле для кода верификации не найдено")
        if len(visible) == 1:
            visible[0].clear()
            visible[0].send_keys(code)
        else:
            for idx, digit in enumerate(code[: len(visible)]):
                visible[idx].clear()
                visible[idx].send_keys(digit)
        self._click_submit()

    def _dismiss_cookie_banner(self) -> None:
        for btn in self._driver.find_elements(By.CSS_SELECTOR, COOKIE_ACCEPT):
            try:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
                    return
            except Exception:
                continue

    def _attach_debug(self, name: str) -> None:
        try:
            allure.attach(
                self._driver.current_url,
                name=f"{name}-url",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                self._driver.title or "",
                name=f"{name}-title",
                attachment_type=allure.attachment_type.TEXT,
            )
            png = self._driver.get_screenshot_as_png()
            allure.attach(png, name=f"{name}-screenshot", attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass

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
