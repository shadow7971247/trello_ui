"""Приватная доска API видна в workspace текущего пользователя."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name
from models.request.create_board import CreateBoardRequest
from pages.workspace_page import WorkspacePage


@allure.epic("Trello Web")
@allure.feature("Workspace")
@allure.story("Видимость доски")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_private_board_visible_in_workspace(
    logged_in: None,
    api_client: TrelloApiClient,
    member_username: str,
) -> None:
    name = board_name("Private UI")
    payload = CreateBoardRequest(name=name, prefs_permission_level="private")
    board = api_client.create_board(payload)

    try:
        with allure.step("UI: приватная доска отображается у владельца"):
            WorkspacePage().open_boards(member_username).should_have_board(name)
    finally:
        api_client.delete_board(board.id)
