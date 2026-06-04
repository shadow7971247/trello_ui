"""UI переименовывает карточку — API проверяет изменение."""

from __future__ import annotations

import allure
import pytest

from api.assertions import assert_card_name
from api_bridge import TrelloApiClient, card_name, prepare_board, prepare_card, prepare_list
from pages.board_page import BoardPage
from pages.card_page import CardPage


@allure.epic("Trello Web")
@allure.feature("Карточки")
@allure.story("Обновление карточки")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
def test_card_rename_via_ui_verified_by_api(
    logged_in: None,
    api_client: TrelloApiClient,
) -> None:
    board = prepare_board(api_client)
    trello_list = prepare_list(api_client, board.id)
    card = prepare_card(api_client, trello_list.id)
    new_name = card_name("Renamed")

    try:
        with allure.step("UI: переименовать карточку"):
            BoardPage().open_by_url(board.url)
            CardPage().open_by_url(card.url).rename(new_name).should_have_title(new_name)

        with allure.step("API: проверить новое имя"):
            updated = api_client.get_card(card.id)
            assert_card_name(updated, new_name)
    finally:
        api_client.delete_board(board.id)
