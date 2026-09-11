import time
from google import genai
from config import API_KEY, AVAILABLE_MODELS, PRIORITY_MODELS

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=API_KEY)
    return _client

def select_model(model_key):
    """Возвращает полное имя модели по ключу или сам ключ, если он уже полное имя."""
    model_name = AVAILABLE_MODELS.get(model_key)
    if model_name is None:
        # возможно, уже передано полное имя
        model_name = model_key
    return model_name

def generate_content(prompt, system_instruction=None, models=None):
    """
    Отправляет запрос к Gemini, перебирая модели из списка.
    :param prompt: текст запроса
    :param system_instruction: системная инструкция (добавляется в начало промпта, т.к. chat не поддерживает отдельно)
    :param models: список ключей моделей (из AVAILABLE_MODELS) или полных имён.
                   Если None, используется PRIORITY_MODELS.
    :return: текст ответа
    """
    client = get_client()
    if models is None:
        models = PRIORITY_MODELS
    # Преобразуем ключи в полные имена
    model_names = [select_model(m) for m in models]

    # Если задана системная инструкция, включаем её в промпт (chat не имеет отдельного параметра)
    full_prompt = prompt
    if system_instruction:
        full_prompt = f"{system_instruction}\n\n{prompt}"

    last_error = None
    for model_name in model_names:
        try:
            print(f"🔄 Пробуем модель: {model_name}")
            # Используем chat-интерфейс (убирает предупреждение)
            chat = client.chats.create(model=model_name)
            response = chat.send_message(full_prompt)
            print(f"✅ Модель {model_name} успешно ответила")
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e)
            # Если ошибка 503 (перегрузка) или 429 (слишком много запросов) — пробуем следующую
            if "503" in error_str or "UNAVAILABLE" in error_str or "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⚠️ Модель {model_name} недоступна ({error_str}). Переключаемся на следующую...")
                time.sleep(1)  # небольшая пауза перед следующей моделью
                continue
            else:
                # Другие ошибки (например, неверный ключ) — сразу бросаем
                raise e

    # Если все модели не ответили
    raise Exception(f"Все модели недоступны. Последняя ошибка: {last_error}")

def analyze_csv_data(csv_text, analysis_type="general", models=None):
    """
    Анализирует CSV-данные, используя первую доступную модель.
    """
    system_prompt = (
        "Ты эксперт по криптовалютному анализу. "
        "Анализируй данные построчно. Для каждой строки выведи: название монеты, цену, объём, изменение за 24ч, "
        "рекомендацию (купить/держать/продать) и краткое обоснование. "
        "Ответ должен быть в виде таблицы с колонками: Монета | Цена | Объём | Изменение% | Рекомендация | Обоснование."
    )
    user_prompt = f"Вот таблица с криптоданными (CSV):\n\n{csv_text}\n\nПроанализируй каждую строку и дай рекомендации."
    
    if analysis_type == "brief":
        user_prompt = f"Дай краткий обзор этих данных (ключевые тренды, самые выгодные монеты):\n\n{csv_text}"
    elif analysis_type == "technical":
        user_prompt = f"Проведи технический анализ данных и дай рекомендации на основе индикаторов:\n\n{csv_text}"
    
    return generate_content(user_prompt, system_instruction=system_prompt, models=models)

def analyze_csv_data_with_context(csv_text, strategy_context, resume_context, history, model_key=None):
    system_instruction = f"""
Ты — трейдер-аналитик, работающий по системе «Модель 66». Вот правила стратегии:
{strategy_context[:2000]}  # укорочено для длины

Текущее состояние портфеля и последние уроки:
{resume_context[:2000]}

История предыдущих сделок (для анализа ошибок):
{str(history)[:1000]}

Твоя задача:
1. Проанализировать все 135 монет из приведённого ниже CSV.
2. Для каждой монеты определить действие: Купить, Держать, Продать (или не входить).
3. Для каждой покупки указать цену входа, стоп-лосс, цель фиксации (тейк-профит), и краткое обоснование (почему именно эта монета, учёт правил стратегии).
4. Отсортировать рекомендации по важности: чем выше вероятность роста (>70%) и лучшее соотношение риск/прибыль, тем выше в списке.
5. Верни результат строго в формате CSV с разделителем «;» и колонками:
   Монета;Действие;Вход;Стоп;Фиксация;Обоснование
   Первая строка — заголовок. Никакого другого текста.
"""
    user_prompt = f"Вот данные по монетам (CSV):\n\n{csv_text}"
    return generate_content(user_prompt, system_instruction=system_instruction, models=None)