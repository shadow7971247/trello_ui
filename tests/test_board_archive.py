"""UI архивирует доску — API проверяет closed=true."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name, prepare_board
from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Доски")
@allure.story("Архивация доски")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
def test_board_archive_via_ui_verified_by_api(
    logged_in: None,
    api_client: TrelloApiClient,
) -> None:
    board = prepare_board(api_client, name=board_name("Archive UI"))

    with allure.step("UI: закрыть доску"):
        BoardPage().open_by_url(board.url).archive_board()

    with allure.step("API: доска в статусе closed"):
        fetched = api_client.get_board(board.id)
        assert fetched.closed is True

    api_client.delete_board(board.id)
