"""Главная страница / список досок пользователя."""

from __future__ import annotations

import os
import time

import allure
from selenium.webdriver.common.by import By
from selene import be, browser, have


class WorkspacePage:
    _SCROLL_STEP = int(os.getenv("WORKSPACE_SCROLL_STEP", "400"))
    _MAX_SCROLLS = int(os.getenv("WORKSPACE_MAX_SCROLLS", "8"))

    def open_home(self) -> WorkspacePage:
        with allure.step("Открыть домашнюю страницу Trello"):
            browser.open("/")
        return self

    def assert_boards_workspace_visible(self) -> WorkspacePage:
        with allure.step("Проверить, что загружена страница досок"):
            selectors = (
                '[data-testid="boards-page"]',
                '[data-testid="your-boards-section"]',
                "main",
            )
            for selector in selectors:
                try:
                    browser.element(selector).should(be.visible)
                    return self
                except Exception:
                    continue
            raise AssertionError(
                "Не найден экран досок (boards-page / your-boards-section / main)"
            )

    def open_boards(self, username: str) -> WorkspacePage:
        with allure.step(f"Открыть доски пользователя {username}"):
            browser.open(f"/u/{username}/boards")
            browser.driver.refresh()
            time.sleep(1)
        return self

    def should_have_board(
        self,
        board_name: str,
        board_url: str | None = None,
        *,
        username: str | None = None,
    ) -> WorkspacePage:
        with allure.step(f"Проверить наличие доски «{board_name}»"):
            if board_url and username:
                with allure.step("Прогреть кэш: открыть доску по URL API"):
                    browser.open(board_url)
                    browser.element('[data-testid="board-name-display"]').should(
                        have.text(board_name)
                    )
                    browser.open(f"/u/{username}/boards")
                    browser.driver.refresh()
                    time.sleep(1)
            self._find_board_element(board_name, board_url=board_url)
        return self

    def should_not_have_board(self, board_name: str) -> WorkspacePage:
        with allure.step(f"Проверить отсутствие доски «{board_name}»"):
            assert self._visible_board_by_name(board_name) is None, (
                f"Доска «{board_name}» всё ещё видна"
            )
        return self

    def open_board(self, board_name: str) -> WorkspacePage:
        with allure.step(f"Открыть доску «{board_name}»"):
            board = self._find_board_element(board_name)
            board.click()
            browser.element('[data-testid="board-name-display"]').should(
                have.text(board_name)
            )
        return self

    def _find_board_element(self, board_name: str, board_url: str | None = None):
        """Ищет доску по имени; при необходимости прокручивает список вниз."""
        for attempt in range(self._MAX_SCROLLS + 1):
            with allure.step(f"Поиск доски (шаг прокрутки {attempt})"):
                board = self._visible_board_by_name(board_name, board_url=board_url)
                if board is not None:
                    return board
                if attempt < self._MAX_SCROLLS:
                    self._scroll_boards_list()
        raise AssertionError(
            f"Доска «{board_name}» не найдена после {self._MAX_SCROLLS} прокруток"
        )

    def _scroll_boards_list(self) -> None:
        scrolled = browser.driver.execute_script(
            """
            const step = arguments[0];
            const selectors = [
              '[data-testid="boards-page"]',
              '[class*="BoardsContainer"]',
              'main',
            ];
            for (const sel of selectors) {
              const el = document.querySelector(sel);
              if (el && el.scrollHeight > el.clientHeight) {
                el.scrollTop += step;
                return true;
              }
            }
            window.scrollBy(0, step);
            return false;
            """,
            self._SCROLL_STEP,
        )
        if not scrolled:
            browser.driver.execute_script(f"window.scrollBy(0, {self._SCROLL_STEP});")

    @staticmethod
    def _board_short_link(board_url: str | None) -> str | None:
        if not board_url or "/b/" not in board_url:
            return None
        return board_url.rstrip("/").split("/b/")[1].split("/")[0]

    def _visible_board_by_name(self, board_name: str, board_url: str | None = None):
        short_link = self._board_short_link(board_url)
        if short_link:
            for element in browser.driver.find_elements(
                By.CSS_SELECTOR, f'a[href*="/b/{short_link}"]'
            ):
                if element.is_displayed():
                    return element

        selectors = (
            '[data-testid="board-name"]',
            'a[href*="/b/"]',
            '[data-testid="board-tile"]',
        )
        for css in selectors:
            for element in browser.driver.find_elements(By.CSS_SELECTOR, css):
                if board_name in (element.text or "") and element.is_displayed():
                    return element
        escaped = board_name.replace("'", "\\'")
        for element in browser.driver.find_elements(
            By.XPATH, f"//*[contains(normalize-space(.), '{escaped}')]"
        ):
            if element.is_displayed() and element.tag_name in ("a", "h3", "div", "span"):
                return element
        return None
