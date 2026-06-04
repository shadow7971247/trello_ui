"""API создаёт карточку — UI проверяет на доске."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, card_name, list_name, prepare_board, prepare_card, prepare_list
from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Карточки")
@allure.story("Создание карточки")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
def test_card_visible_after_api_creation(
    logged_in: None,
    api_client: TrelloApiClient,
) -> None:
    board = prepare_board(api_client)
    trello_list = prepare_list(api_client, board.id, name=list_name("UI List"))
    card = prepare_card(api_client, trello_list.id, name=card_name("UI Card"))

    try:
        with allure.step("UI: открыть доску и проверить карточку"):
            (
                BoardPage()
                .open_by_url(board.url or f"https://trello.com/b/{board.id}")
                .should_have_board_title(board.name)
                .should_have_list(trello_list.name)
                .should_have_card(card.name)
            )
    finally:
        api_client.delete_board(board.id)
