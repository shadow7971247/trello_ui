"""Карточка Trello — read-only проверки на публичной доске."""

from __future__ import annotations

import allure
from selene import be, browser, have
from selenium.webdriver.common.by import By

from ui_utils.screenshot import capture_step


class CardPage:
    _TITLE = '[data-testid="card-back-name-input"], [data-testid="card-back-title"]'

    def open_by_url(self, url: str) -> CardPage:
        step = f"Открыть карточку по URL: {url}"
        with allure.step(step):
            browser.open(url)
            browser.wait.until(lambda _: "/c/" in browser.driver.current_url)
            browser.element(self._TITLE).should(be.visible)
            capture_step(step)
        return self

    def should_have_title(self, title: str) -> CardPage:
        step = f"Проверить название карточки «{title}»"
        with allure.step(step):
            browser.element(self._TITLE).should(have.text(title))
            capture_step(step)
        return self

    def close(self) -> CardPage:
        step = "Закрыть окно карточки"
        with allure.step(step):
            for selector in (
                '[data-testid="card-back-close-button"]',
                'button[aria-label="Close dialog"]',
                'button[aria-label="Закрыть"]',
            ):
                buttons = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed():
                        button.click()
                        capture_step(step)
                        return self
        return self
