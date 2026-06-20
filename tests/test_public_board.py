"""Публичная доска: открытие по URL без логина."""

from __future__ import annotations

import allure
import pytest

from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Открытие доски")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_public_board_opens_by_url(public_test_board) -> None:
    board = public_test_board("Public UI")

    with allure.step("UI: открыть публичную доску"):
        (
            BoardPage()
            .open_by_url(board.url)
            .should_be_public_view()
            .should_have_board_title(board.name)
        )


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Short URL")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_board_opens_by_short_url(public_test_board) -> None:
    board = public_test_board("Public Short")

    with allure.step("UI: открыть доску по shortUrl"):
        assert board.short_url
        (
            BoardPage()
            .open_by_url(board.short_url)
            .should_be_public_view()
            .should_have_board_title(board.name)
        )


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Заголовок вкладки")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_board_title_in_browser_tab(public_test_board) -> None:
    board = public_test_board("Public Tab")

    with allure.step("UI: имя доски отображается в title вкладки"):
        (
            BoardPage()
            .open_by_url(board.url)
            .should_be_public_view()
            .should_have_title_in_browser_tab(board.name)
        )
