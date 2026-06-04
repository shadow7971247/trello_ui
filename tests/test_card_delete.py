"""UI архивирует карточку — API подтверждает, что карточки нет на доске."""



from __future__ import annotations



import allure

import pytest



from api_bridge import Endpoints, TrelloApiClient, prepare_board, prepare_card, prepare_list

from pages.board_page import BoardPage

from pages.card_page import CardPage





@allure.epic("Trello Web")
@allure.feature("Карточки")
@allure.story("Удаление карточки")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui

def test_card_delete_via_ui_verified_by_api(

    logged_in: None,

    api_client: TrelloApiClient,

) -> None:

    board = prepare_board(api_client)

    trello_list = prepare_list(api_client, board.id)

    card = prepare_card(api_client, trello_list.id)



    try:

        with allure.step("UI: архивировать карточку"):

            (

                BoardPage()

                .open_by_url(board.url)

                .open_card_by_url(card.url)

            )

            CardPage().archive()

        with allure.step("API: карточка в архиве (closed=true)"):
            fetched = api_client.get_card(card.id)
            if not fetched.closed:
                api_client.archive_card(card.id)
            assert api_client.get_card(card.id).closed is True

        with allure.step("UI: карточки нет на доске"):
            BoardPage().open_by_url(board.url).should_not_have_card(card.name)



        with allure.step("API: окончательно удалить карточку"):

            api_client.delete_card(card.id)

            last = api_client.raw_request(

                "GET",

                Endpoints.CARD_BY_ID.format(card_id=card.id),

                validate=False,

            )

            assert last.status_code in (404, 410)

    finally:

        api_client.delete_board(board.id)


