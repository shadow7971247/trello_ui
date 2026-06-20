"""Публичная доска: карточки и ссылки без логина."""

from __future__ import annotations

import allure
import pytest

from api_bridge import prepare_card, prepare_list
from pages.board_page import BoardPage


def _ascii_card_name(label: str) -> str:
    return f"UI {label} card"


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Ссылка на карточку")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_public_card_has_trello_link(public_test_board, api_client) -> None:
    board = public_test_board("Link")
    trello_list = prepare_list(api_client, board.id)
    name = _ascii_card_name("link")
    card = prepare_card(api_client, trello_list.id, name=name, desc="API setup")

    with allure.step("UI: карточка на доске имеет ссылку /c/"):
        (
            BoardPage()
            .open_by_url(board.url)
            .should_be_public_view()
            .should_have_card(name)
            .should_have_card_link(name)
        )
    with allure.step("API: shortUrl карточки существует"):
        assert card.short_url and "/c/" in card.short_url


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Карточка на доске")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_ascii_card_visible_on_board(public_test_board, api_client) -> None:
    board = public_test_board("Ascii")
    trello_list = prepare_list(api_client, board.id)
    name = _ascii_card_name("ascii")
    prepare_card(api_client, trello_list.id, name=name, desc="visible to guests")

    with allure.step("UI: ASCII-имя карточки видно гостю"):
        (
            BoardPage()
            .open_by_url(board.url)
            .should_be_public_view()
            .should_have_card(name)
        )


@allure.epic("Trello Web")
@allure.feature("Публичные доски")
@allure.story("Несколько карточек")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
def test_public_card_links_for_multiple_cards(public_test_board, api_client) -> None:
    board = public_test_board("Links")
    trello_list = prepare_list(api_client, board.id)
    first = _ascii_card_name("one")
    second = _ascii_card_name("two")
    prepare_card(api_client, trello_list.id, name=first)
    prepare_card(api_client, trello_list.id, name=second)

    with allure.step("UI: обе карточки имеют ссылки"):
        page = BoardPage().open_by_url(board.url).should_be_public_view()
        page.should_have_card_link(first).should_have_card_link(second)
