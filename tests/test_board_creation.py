"""API создаёт доску — UI проверяет отображение."""

from __future__ import annotations

import allure
import pytest

from api_bridge import board_name, prepare_board
from api_bridge import TrelloApiClient
from pages.workspace_page import WorkspacePage


@allure.epic("Trello Web")
@allure.feature("Доски")
@allure.story("Создание доски")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_board_visible_after_api_creation(
    logged_in: None,
    api_client: TrelloApiClient,
    member_username: str,
) -> None:
    name = board_name("UI Board")
    board = prepare_board(api_client, name=name)

    try:
        with allure.step("UI: найти доску в workspace"):
            (
                WorkspacePage()
                .open_boards(member_username)
                .should_have_board(name, board.url, username=member_username)
            )
    finally:
        api_client.delete_board(board.id)
