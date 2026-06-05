"""Подключение клиента trello_api (соседний клон или TRELLO_API_PATH)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _resolve_api_root() -> Path:
    env_path = os.getenv("TRELLO_API_PATH", "").strip()
    if env_path:
        return Path(env_path).resolve()
    sibling = Path(__file__).resolve().parent.parent / "trello_api"
    if sibling.is_dir():
        return sibling
    raise FileNotFoundError(
        "Не найден trello_api. Клонируйте репозиторий рядом (../trello_api) "
        "или задайте TRELLO_API_PATH в CI."
    )


TRELLO_API_ROOT = _resolve_api_root()
if str(TRELLO_API_ROOT) not in sys.path:
    sys.path.append(str(TRELLO_API_ROOT))

from api.client import TrelloApiClient  # noqa: E402
from api.endpoints import Endpoints  # noqa: E402
from fixtures.generators import (  # noqa: E402
    board_name,
    card_description,
    card_name,
    list_name,
    prepare_board,
    prepare_card,
    prepare_list,
    prepare_public_board,
)
from utils.config import Config as ApiConfig  # noqa: E402

__all__ = [
    "TrelloApiClient",
    "Endpoints",
    "ApiConfig",
    "board_name",
    "list_name",
    "card_name",
    "card_description",
    "prepare_board",
    "prepare_public_board",
    "prepare_list",
    "prepare_card",
    "TRELLO_API_ROOT",
]
