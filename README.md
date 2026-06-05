# trello-ui-tests

UI-автотесты Trello (Selenium + Selene). **Без логина в браузере**: API создаёт **публичные** доски, UI проверяет отображение по прямому URL.

Экосистема: **trello_api** (CRUD + auth) → **trello_ui** (read-only web) → **trello_mobile** (native app). CI: [docs/CI.md](docs/CI.md).

## Стек

- Python 3.12+
- Pytest, Selene, Selenium
- Allure, python-dotenv
- Клон **trello_api** рядом или `TRELLO_API_PATH` в CI

## Установка

```bash
cd trello_ui
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

В `.env` нужны только **API key/token** (как в trello_api). Email и пароль Trello для UI **не требуются**.

## Запуск

```bash
pytest
pytest -m smoke
pytest -m ui
```

## Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## Сценарии (11 тестов, без логина)

| Файл | Что проверяет |
|------|----------------|
| `test_public_board` | Открытие по URL / shortUrl, описание доски |
| `test_public_lists` | Один и несколько списков |
| `test_public_cards` | Карточки на доске, скрытие архивной |
| `test_public_card_detail` | Карточка по URL, описание, клик с доски |

Мутации (rename, archive, delete) — в **trello_api**.

## Структура

```
pages/          # BoardPage, CardPage (read-only)
tests/          # публичные сценарии
config.py       # API + browser
conftest.py     # browser, api_client
api_bridge.py   # импорт trello_api
```
