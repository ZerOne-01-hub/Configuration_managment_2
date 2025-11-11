#!/usr/bin/env python3
"""
CLI-приложение для визуализации графа зависимостей пакетов.
Этап 1: Минимальный прототип с конфигурацией.
"""
import sys
import argparse
from config_parser import ConfigParser, ConfigError


def print_config(config: dict) -> None:
    """
    Выводит все параметры конфигурации в формате ключ-значение.
    
    Args:
        config: Словарь с параметрами конфигурации
    """
    print("=" * 60)
    print("Параметры конфигурации:")
    print("=" * 60)
    
    for key, value in config.items():
        # Форматирование булевых значений
        if isinstance(value, bool):
            value_str = "true" if value else "false"
        else:
            value_str = str(value) if value else "(пусто)"
        
        print(f"{key}: {value_str}")
    
    print("=" * 60)


def main():
    """Основная функция приложения."""
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов"
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.yaml',
        help='Путь к конфигурационному файлу (по умолчанию: config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        # Загрузка и валидация конфигурации
        config_parser = ConfigParser(args.config)
        config = config_parser.load_config()
        
        # Вывод всех параметров конфигурации
        print_config(config)
        
        return 0
        
    except ConfigError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

