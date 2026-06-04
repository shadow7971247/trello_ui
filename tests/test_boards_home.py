"""Smoke: авторизованный пользователь видит страницу досок."""

from __future__ import annotations

import allure
import pytest

from pages.workspace_page import WorkspacePage


@allure.epic("Trello Web")
@allure.feature("Workspace")
@allure.story("Страница досок")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@pytest.mark.smoke
def test_boards_page_visible_for_logged_in_user(
    logged_in: None,
    member_username: str,
) -> None:
    with allure.step("Открыть список досок пользователя"):
        WorkspacePage().open_boards(member_username).assert_boards_workspace_visible()
