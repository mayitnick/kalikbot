import json
import os
from typing import Union

# Имя файла для хранения статистики
STATS_FILE = 'statistics.json'

def _load_stats() -> dict:
    """Загружает статистику из JSON файла"""
    if not os.path.exists(STATS_FILE):
        return {}
    
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _save_stats(stats: dict) -> None:
    """Сохраняет статистику в JSON файл"""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def add_statistic(name_of_statistic: str, value: Union[int, float] = 1) -> None:
    """
    Добавляет значение к статистике
    
    Args:
        name_of_statistic: название статистики
        value: значение для добавления (по умолчанию 1)
    """
    stats = _load_stats()
    
    if name_of_statistic in stats:
        # Если статистика уже существует, добавляем значение
        stats[name_of_statistic] += value
    else:
        # Если статистики нет, создаем новую
        stats[name_of_statistic] = value
    
    _save_stats(stats)

def view_statistic(name_of_statistic: str) -> Union[int, float, None]:
    """
    Просматривает значение определенной статистики
    
    Args:
        name_of_statistic: название статистики
        
    Returns:
        Значение статистики или None, если статистика не найдена
    """
    stats = _load_stats()
    return stats.get(name_of_statistic)

def view_all_statistics() -> dict:
    """
    Просматривает всю статистику
    
    Returns:
        Словарь со всей статистикой
    """
    return _load_stats()

def reset_statistic(name_of_statistic: str = None) -> None:
    """
    Сбрасывает статистику
    
    Args:
        name_of_statistic: название статистики для сброса 
                          (если None - сбрасывает всю статистику)
    """
    if name_of_statistic is None:
        # Сброс всей статистики
        _save_stats({})
    else:
        # Сброс конкретной статистики
        stats = _load_stats()
        if name_of_statistic in stats:
            del stats[name_of_statistic]
            _save_stats(stats)
