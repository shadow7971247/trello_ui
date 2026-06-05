"""Публичная доска: открытие по URL без логина."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name, prepare_public_board
from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Открытие доски")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_public_board_opens_by_url(api_client: TrelloApiClient) -> None:
    name = board_name("Public UI")
    board = prepare_public_board(api_client, name=name)

    try:
        with allure.step("UI: открыть публичную доску"):
            (
                BoardPage()
                .open_by_url(board.url or "")
                .should_be_public_view()
                .should_have_board_title(name)
            )
    finally:
        api_client.delete_board(board.id)


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Short URL")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_board_opens_by_short_url(api_client: TrelloApiClient) -> None:
    name = board_name("Public Short")
    board = prepare_public_board(api_client, name=name)

    try:
        with allure.step("UI: открыть доску по shortUrl"):
            assert board.short_url
            (
                BoardPage()
                .open_by_url(board.short_url)
                .should_be_public_view()
                .should_have_board_title(name)
            )
    finally:
        api_client.delete_board(board.id)


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Заголовок вкладки")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_board_title_in_browser_tab(api_client: TrelloApiClient) -> None:
    name = board_name("Public Tab")
    board = prepare_public_board(api_client, name=name)

    try:
        with allure.step("UI: имя доски отображается в title вкладки"):
            (
                BoardPage()
                .open_by_url(board.url or "")
                .should_be_public_view()
                .should_have_title_in_browser_tab(name)
            )
    finally:
        api_client.delete_board(board.id)
