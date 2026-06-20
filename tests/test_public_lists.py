"""Публичная доска: списки без логина."""

from __future__ import annotations

import allure
import pytest

from api_bridge import list_name, prepare_list
from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Списки")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_public_list_visible_on_board(public_test_board, api_client) -> None:
    board = public_test_board("Lists")
    trello_list = prepare_list(api_client, board.id, name=list_name("Public List"))

    with allure.step("UI: список виден на публичной доске"):
        (
            BoardPage()
            .open_by_url(board.url)
            .should_be_public_view()
            .should_have_list(trello_list.name)
        )


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Списки")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_multiple_lists_visible(public_test_board, api_client) -> None:
    board = public_test_board("MultiList")
    first = prepare_list(api_client, board.id, name=list_name("Alpha"))
    second = prepare_list(api_client, board.id, name=list_name("Beta"))

    with allure.step("UI: оба списка видны гостю"):
        page = BoardPage().open_by_url(board.url).should_be_public_view()
        page.should_have_list(first.name).should_have_list(second.name)
