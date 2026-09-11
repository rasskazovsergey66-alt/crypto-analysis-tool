import requests
import pandas as pd
from io import StringIO
from config import GITHUB_TOKEN

def get_github_headers():
    """Возвращает заголовки для запросов к GitHub API (с авторизацией, если токен задан)."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def get_latest_csv_url(repo_owner, repo_name, path=""):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = get_github_headers()
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    files = response.json()
    csv_files = [f for f in files if f['name'].endswith('.csv')]
    if not csv_files:
        raise Exception("CSV-файлы в репозитории не найдены.")

    # Сортируем по имени файла (в нём есть дата) — берём последний
    latest_file = max(csv_files, key=lambda f: f['name'])
    return latest_file['download_url']

def load_crypto_data_from_github(repo_owner, repo_name, path=""):
    """
    Загружает данные из самого свежего CSV-файла в репозитории.
    Возвращает pandas DataFrame.
    """
    csv_url = get_latest_csv_url(repo_owner, repo_name, path)
    headers = get_github_headers()  # для raw-запроса токен не обязателен, но можно добавить
    response = requests.get(csv_url, headers=headers)
    response.raise_for_status()
    
    csv_data = StringIO(response.text)
    # ВАЖНО: разделитель — точка с запятой
    df = pd.read_csv(csv_data, sep=';')
    return df