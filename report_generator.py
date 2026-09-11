import pandas as pd
from datetime import datetime

def save_recommendations_xls(recommendations_df, prefix="recommendations"):
    """Сохраняет DataFrame с рекомендациями в XLSX"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        recommendations_df.to_excel(writer, sheet_name='Рекомендации', index=False)
    return filename

def save_history_analysis_xls(analysis_df, prefix="history_analysis"):
    """Сохраняет анализ предыдущих сделок"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        analysis_df.to_excel(writer, sheet_name='Анализ истории', index=False)
    return filename