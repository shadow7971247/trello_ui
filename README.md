# trello-ui-tests

UI-автотесты Trello (Selenium + Selene). **API-first**: `trello_api` готовит данные, UI проверяет отображение и действия пользователя.

Экосистема: **trello_api** (данные) → **trello_ui** → **trello_mobile**. CI: [docs/CI.md](docs/CI.md).

## Стек

- Python 3.12+
- Pytest, Selene, Selenium
- Allure, python-dotenv
- Клон **trello_api** рядом или `TRELLO_API_PATH` в CI (клиент, generators, модели)

## Установка

```bash
cd trello_ui
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
```

Заполните `.env`: учётные данные Trello/Atlassian и API key/token (см. репозиторий **trello_api**).

Установите ChromeDriver / GeckoDriver, совместимый с браузером.

## Запуск

```bash
pytest
pytest -m smoke
pytest tests/test_card_update.py
```

## Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## Сценарии

| Тест | Стратегия |
|------|-----------|
| `test_board_creation` | API → доска видна в workspace |
| `test_card_creation` | API → карточка на доске |
| `test_card_update` | UI rename → API проверяет имя |
| `test_card_delete` | UI delete → API 404 |
| `test_board_archive` | UI close board → API `closed` |
| `test_workspace_visibility` | приватная доска видна владельцу |

## Структура

```
pages/          # Page Object
tests/          # сценарии
config.py       # .env
conftest.py     # browser, api_client, login
api_bridge.py   # импорт trello_api
```
