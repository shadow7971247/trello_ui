"""Публичная доска Trello — read-only проверки без логина."""

from __future__ import annotations

import allure
from selenium.webdriver.common.by import By
from selene import be, browser, have

from ui_utils.screenshot import capture_step


class BoardPage:
    _LOGIN_HOSTS = ("id.atlassian.com", "trello.com/login")

    def open_by_url(self, url: str) -> BoardPage:
        step = f"Открыть доску по URL: {url}"
        with allure.step(step):
            browser.open(url)
            self._wait_board_loaded()
            capture_step(step)
        return self

    def should_be_public_view(self) -> BoardPage:
        step = "Проверить, что открыта доска без редиректа на логин"
        with allure.step(step):
            current_url = browser.driver.current_url
            assert current_url, "URL страницы пустой"
            url_lower = current_url.lower()
            assert not any(host in url_lower for host in self._LOGIN_HOSTS), (
                f"Редирект на логин: {current_url}"
            )
            browser.element('[data-testid="board-name-display"]').should(be.visible)
            capture_step(step)
        return self

    def should_have_board_title(self, title: str) -> BoardPage:
        step = f"Проверить заголовок доски «{title}»"
        with allure.step(step):
            browser.element('[data-testid="board-name-display"]').should(have.text(title))
            capture_step(step)
        return self

    def should_have_title_in_browser_tab(self, title: str) -> BoardPage:
        step = f"Проверить заголовок вкладки браузера: «{title}»"
        with allure.step(step):
            browser.wait.until(lambda _: title.lower() in browser.driver.title.lower())
            capture_step(step)
        return self

    def should_have_card_link(self, card_name: str) -> BoardPage:
        step = f"Проверить ссылку на карточку «{card_name}»"
        with allure.step(step):
            card = self._find_by_testid_text("card-name", card_name)
            assert card is not None, f"Карточка «{card_name}» не найдена"
            link = self._card_link(card)
            href = link.get_attribute("href")
            assert href and "/c/" in href, f"У карточки нет ссылки /c/: {href!r}"
            capture_step(step)
        return self

    def should_have_list(self, list_name: str) -> BoardPage:
        step = f"Проверить список «{list_name}»"
        with allure.step(step):
            assert self._find_by_testid_text("list", list_name), (
                f"Список «{list_name}» не найден на доске"
            )
            capture_step(step)
        return self

    def should_have_card(self, card_name: str) -> BoardPage:
        step = f"Проверить карточку «{card_name}» на доске"
        with allure.step(step):
            assert self._find_by_testid_text("card-name", card_name), (
                f"Карточка «{card_name}» не найдена на доске"
            )
            capture_step(step)
        return self

    def should_not_have_card(self, card_name: str) -> BoardPage:
        step = f"Проверить отсутствие карточки «{card_name}»"
        with allure.step(step):
            browser.driver.refresh()
            self._wait_board_loaded()
            assert not self._find_by_testid_text("card-name", card_name), (
                f"Карточка «{card_name}» всё ещё на доске"
            )
            capture_step(step)
        return self

    def open_card(self, card_name: str) -> BoardPage:
        step = f"Открыть карточку «{card_name}»"
        with allure.step(step):
            card = self._find_by_testid_text("card-name", card_name)
            assert card is not None, f"Карточка «{card_name}» не найдена"
            self._card_link(card).click()
            browser.wait.until(lambda _: "/c/" in browser.driver.current_url)
            capture_step(step)
        return self

    @staticmethod
    def _card_link(card) -> object:
        if card.tag_name == "a":
            return card
        return card.find_element(By.XPATH, "ancestor-or-self::a[contains(@href, '/c/')]")

    def _wait_board_loaded(self) -> None:
        browser.element('[data-testid="board-name-display"]').should(be.visible)

    @staticmethod
    def _find_by_testid_text(testid: str, text: str):
        for element in browser.driver.find_elements(
            By.CSS_SELECTOR, f'[data-testid="{testid}"]'
        ):
            if text in element.text and element.is_displayed():
                return element
        return None
