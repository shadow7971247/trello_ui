"""Публичная доска: списки без логина."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, list_name, prepare_list, prepare_public_board
from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Списки")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_public_list_visible_on_board(api_client: TrelloApiClient) -> None:
    board = prepare_public_board(api_client)
    trello_list = prepare_list(api_client, board.id, name=list_name("Public List"))

    try:
        with allure.step("UI: список виден на публичной доске"):
            (
                BoardPage()
                .open_by_url(board.url or "")
                .should_be_public_view()
                .should_have_list(trello_list.name)
            )
    finally:
        api_client.delete_board(board.id)


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Списки")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_multiple_lists_visible(api_client: TrelloApiClient) -> None:
    board = prepare_public_board(api_client)
    first = prepare_list(api_client, board.id, name=list_name("Alpha"))
    second = prepare_list(api_client, board.id, name=list_name("Beta"))

    try:
        with allure.step("UI: оба списка видны гостю"):
            page = BoardPage().open_by_url(board.url or "").should_be_public_view()
            page.should_have_list(first.name).should_have_list(second.name)
    finally:
        api_client.delete_board(board.id)
