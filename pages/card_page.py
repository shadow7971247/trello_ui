"""Карточка Trello — read-only проверки на публичной доске."""

from __future__ import annotations

import allure
from selene import browser
from selenium.webdriver.common.by import By

from ui_utils.ui_attach import add_screenshot


class CardPage:
    @staticmethod
    def _capture(step_name: str) -> None:
        add_screenshot(browser.driver, step_name)

    def open_by_url(self, url: str) -> CardPage:
        step = f"Открыть карточку по URL: {url}"
        with allure.step(step):
            browser.open(url)
            browser.wait.until(lambda _: "/c/" in (browser.driver.current_url or ""))
            browser.wait.until(lambda _: self._card_back_ready())
            self._capture(step)
        return self

    @staticmethod
    def _card_back_ready() -> bool:
        return bool(
            browser.driver.execute_script(
                """
                const root = document.querySelector('#react-root-card-back')
                  || document.querySelector('#layer-manager-card-back');
                if (!root) return false;
                return root.innerText.trim().length > 0;
                """
            )
        )

    def should_have_title(self, title: str) -> CardPage:
        step = f"Проверить название карточки «{title}»"
        with allure.step(step):
            needle = title.lower()

            def _found() -> bool:
                page_title = (browser.driver.title or "").lower()
                if needle in page_title:
                    return True
                body = browser.driver.find_element(By.TAG_NAME, "body").text.lower()
                return needle in body

            browser.wait.until(lambda _: _found())
            self._capture(step)
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
                        self._capture(step)
                        return self
        return self
