"""Карточка Trello — read-only проверки на публичной доске."""

from __future__ import annotations

import allure
from selene import browser
from selenium.webdriver.common.by import By


class CardPage:
    def open_by_url(self, url: str) -> CardPage:
        with allure.step(f"Открыть карточку по URL: {url}"):
            browser.open(url)
            browser.wait.until(lambda _: "/c/" in (browser.driver.current_url or ""))
            browser.wait.until(lambda _: self._card_back_ready())
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
        with allure.step(f"Проверить название карточки «{title}»"):
            needle = title.lower()

            def _found() -> bool:
                page_title = (browser.driver.title or "").lower()
                if needle in page_title:
                    return True
                body = browser.driver.find_element(By.TAG_NAME, "body").text.lower()
                return needle in body

            browser.wait.until(lambda _: _found())
        return self

    def close(self) -> CardPage:
        with allure.step("Закрыть окно карточки"):
            for selector in (
                '[data-testid="card-back-close-button"]',
                'button[aria-label="Close dialog"]',
                'button[aria-label="Закрыть"]',
            ):
                buttons = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed():
                        button.click()
                        return self
        return self
