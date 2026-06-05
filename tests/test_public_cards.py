"""Публичная доска: карточки без логина."""

from __future__ import annotations

import allure
import pytest

from api_bridge import (
    TrelloApiClient,
    card_name,
    list_name,
    prepare_card,
    prepare_list,
    prepare_public_board,
)
from pages.board_page import BoardPage


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Карточки на доске")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_public_card_visible_on_board(api_client: TrelloApiClient) -> None:
    board = prepare_public_board(api_client)
    trello_list = prepare_list(api_client, board.id, name=list_name("Cards"))
    card = prepare_card(api_client, trello_list.id, name=card_name("Visible"))

    try:
        with allure.step("UI: карточка видна на публичной доске"):
            (
                BoardPage()
                .open_by_url(board.url or "")
                .should_be_public_view()
                .should_have_card(card.name)
            )
    finally:
        api_client.delete_board(board.id)


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Карточки на доске")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_multiple_cards_visible(api_client: TrelloApiClient) -> None:
    board = prepare_public_board(api_client)
    trello_list = prepare_list(api_client, board.id)
    first = prepare_card(api_client, trello_list.id, name=card_name("One"))
    second = prepare_card(api_client, trello_list.id, name=card_name("Two"))

    try:
        with allure.step("UI: несколько карточек видны гостю"):
            page = BoardPage().open_by_url(board.url or "").should_be_public_view()
            page.should_have_card(first.name).should_have_card(second.name)
    finally:
        api_client.delete_board(board.id)


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Архив карточки")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_archived_card_hidden_on_board(api_client: TrelloApiClient) -> None:
    board = prepare_public_board(api_client)
    trello_list = prepare_list(api_client, board.id)
    card = prepare_card(api_client, trello_list.id, name=card_name("Archive"))

    try:
        with allure.step("API: архивировать карточку"):
            api_client.archive_card(card.id)

        with allure.step("UI: архивная карточка не отображается"):
            (
                BoardPage()
                .open_by_url(board.url or "")
                .should_be_public_view()
                .should_not_have_card(card.name)
            )
    finally:
        api_client.delete_board(board.id)
