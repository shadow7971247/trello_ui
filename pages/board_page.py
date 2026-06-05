"""Публичная доска Trello — read-only проверки без логина."""

from __future__ import annotations

import time

import allure
from selenium.webdriver.common.by import By
from selene import be, browser, have


class BoardPage:
    _LOGIN_HOSTS = ("id.atlassian.com", "trello.com/login")

    def open_by_url(self, url: str) -> BoardPage:
        with allure.step(f"Открыть доску по URL: {url}"):
            browser.open(url)
            self._wait_board_loaded()
        return self

    def should_be_public_view(self) -> BoardPage:
        with allure.step("Проверить, что открыта доска без редиректа на логин"):
            url = (browser.driver.current_url or "").lower()
            assert not any(host in url for host in self._LOGIN_HOSTS), (
                f"Редирект на логин: {browser.driver.current_url}"
            )
            browser.element('[data-testid="board-name-display"]').should(be.visible)
        return self

    def should_have_board_title(self, title: str) -> BoardPage:
        with allure.step(f"Проверить заголовок доски «{title}»"):
            browser.element('[data-testid="board-name-display"]').should(have.text(title))
        return self

    def should_have_title_in_browser_tab(self, title: str) -> BoardPage:
        with allure.step(f"Проверить заголовок вкладки браузера: «{title}»"):
            browser.wait.until(lambda _: title.lower() in (browser.driver.title or "").lower())
        return self

    def should_have_card_link(self, card_name: str) -> BoardPage:
        with allure.step(f"Проверить ссылку на карточку «{card_name}»"):
            card = self._find_by_testid_text("card-name", card_name)
            assert card, f"Карточка «{card_name}» не найдена"
            href = card.get_attribute("href") or ""
            if not href and card.tag_name != "a":
                try:
                    link = card.find_element(By.XPATH, "ancestor-or-self::a[contains(@href, '/c/')]")
                    href = link.get_attribute("href") or ""
                except Exception:
                    href = ""
            assert "/c/" in href, f"У карточки нет ссылки /c/: {href!r}"
        return self

    def should_have_list(self, list_name: str) -> BoardPage:
        with allure.step(f"Проверить список «{list_name}»"):
            assert self._find_by_testid_text("list", list_name), (
                f"Список «{list_name}» не найден на доске"
            )
        return self

    def should_have_card(self, card_name: str) -> BoardPage:
        with allure.step(f"Проверить карточку «{card_name}» на доске"):
            assert self._find_by_testid_text("card-name", card_name), (
                f"Карточка «{card_name}» не найдена на доске"
            )
        return self

    def should_not_have_card(self, card_name: str) -> BoardPage:
        with allure.step(f"Проверить отсутствие карточки «{card_name}»"):
            for attempt in range(6):
                if not self._find_by_testid_text("card-name", card_name):
                    return self
                if attempt < 5:
                    browser.driver.refresh()
                    self._wait_board_loaded()
                    time.sleep(1)
            raise AssertionError(f"Карточка «{card_name}» всё ещё на доске")
        return self

    def open_card(self, card_name: str) -> BoardPage:
        with allure.step(f"Открыть карточку «{card_name}»"):
            card = self._find_by_testid_text("card-name", card_name)
            assert card, f"Карточка «{card_name}» не найдена"
            link = card
            if getattr(card, "tag_name", "") != "a":
                try:
                    link = card.find_element(By.XPATH, "ancestor-or-self::a[contains(@href, '/c/')]")
                except Exception:
                    link = card
            link.click()
            browser.wait.until(
                lambda _: "/c/" in (browser.driver.current_url or "")
                or bool(
                    browser.driver.find_elements(
                        By.CSS_SELECTOR,
                        "div#layer-manager-card-back, div.window-overlay, #react-root-card-back",
                    )
                )
            )
        return self

    def _wait_board_loaded(self) -> None:
        browser.element('[data-testid="board-name-display"]').should(be.visible)

    @staticmethod
    def _find_by_testid_text(testid: str, text: str):
        for element in browser.driver.find_elements(
            By.CSS_SELECTOR, f'[data-testid="{testid}"]'
        ):
            if text in (element.text or "") and element.is_displayed():
                return element
        return None
