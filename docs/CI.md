# CI: Jenkins + Allure TestOps

Репозиторий **trello_ui** — UI-стадия после API.

## Зависимость от trello_api

В job клонируйте **trello_api** в соседнюю папку или задайте:

```text
TRELLO_API_PATH=C:\jenkins\workspace\trello_api
```

## Jenkins (этот репозиторий)

```bash
pip install -r requirements.txt
pytest -m "not browserstack" --alluredir=allure-results
# или:
pytest -m ui --alluredir=allure-results
```

Секреты: `TRELLO_*`, API key/token (см. `.env.example`).

## Allure TestOps

```bash
allurectl upload --endpoint %ALLURE_ENDPOINT% ^
  --token %ALLURE_TOKEN% ^
  --project-id %ALLURE_PROJECT_ID% ^
  --launch-name "trello-ui-%BUILD_NUMBER%" ^
  allure-results
```
