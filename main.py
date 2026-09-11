import datetime
import os
import pandas as pd
from data_loader import load_crypto_data_from_github
from gemini_client import analyze_csv_data_with_context
from context_loader import get_strategy_context
from report_generator import save_recommendations_xls, save_history_analysis_xls
from history_manager import load_history
from config import REPO_OWNER, REPO_NAME

def main():
    print("🚀 Загружаем данные...")
    df = load_crypto_data_from_github(REPO_OWNER, REPO_NAME)
    print(f"✅ Загружено {len(df)} записей.")
    csv_text = df.to_csv(sep=';', index=False)

    context = get_strategy_context()
    strategy_text = context.get('strategy', '')
    resume_text = context.get('resume', '')
    if not strategy_text and not resume_text:
        print("⚠️ Контекст стратегии не загружен. Будут использованы общие настройки.")

    history = load_history()
    print("🧠 Запрашиваем рекомендации с учётом контекста...")
    recommendations_text = analyze_csv_data_with_context(
        csv_text,
        strategy_context=strategy_text,
        resume_context=resume_text,
        history=history
    )

    # Парсим ответ модели (ожидаем CSV с разделителем ;)
    lines = recommendations_text.strip().split('\n')
    data_rows = []
    for line in lines[1:]:
        parts = line.split(';')
        if len(parts) >= 6:
            data_rows.append(parts)
    columns = ['Монета', 'Действие', 'Вход', 'Стоп', 'Фиксация', 'Обоснование']
    rec_df = pd.DataFrame(data_rows, columns=columns)

    # Сортировка по приоритету
    priority = {'Купить': 0, 'Держать': 1, 'Продать': 2}
    rec_df['priority'] = rec_df['Действие'].map(priority).fillna(3)
    rec_df = rec_df.sort_values('priority').drop('priority', axis=1)

    xls_file = save_recommendations_xls(rec_df)
    print(f"✅ Рекомендации сохранены в {xls_file}")

    analysis_file = None
    if history:
        hist_df = pd.DataFrame(history)
        hist_df['Результат'] = 'Ожидает проверки'
        analysis_file = save_history_analysis_xls(hist_df)
        print(f"✅ Анализ истории сохранён в {analysis_file}")
    else:
        print("ℹ️ История сделок пуста, анализ не выполнен.")

    # Генерация резюме
    analysis_file_str = analysis_file if analysis_file else 'нет'
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    resume_md = f"""
# Резюме чата — срез {datetime.datetime.now().strftime('%d.%m.%Y, %H:%M МСК')}

## 1. Контекст
- Стратегия: Модель 66 (описана в analiz_epohi...)
- Текущие открытые позиции: {len(rec_df[rec_df['Действие'] == 'Держать'])} линий
- Рекомендовано новых входов: {len(rec_df[rec_df['Действие'] == 'Купить'])}
- Карантины и лимиты описаны в деталях.

## 2. Рекомендации
{rec_df.to_string(index=False)}

## 3. План на следующий срез
- Проверить исполнение лимитных ордеров.
- Подтянуть стопы по триггерам.
- При изменении режима BTC скорректировать экспозицию.

## 4. Файлы
- Рекомендации: {xls_file}
- Анализ истории: {analysis_file_str}
"""
    resume_filename = f"rezume_chata_{timestamp}.md"
    with open(resume_filename, 'w', encoding='utf-8') as f:
        f.write(resume_md)
    print(f"✅ Резюме чата создано: {resume_filename}")

if __name__ == "__main__":
    main()