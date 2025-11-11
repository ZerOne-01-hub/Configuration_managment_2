#!/usr/bin/env python3
"""
CLI-приложение для визуализации графа зависимостей пакетов.
Этап 3: Основные операции.
"""
import sys
import argparse
from config_parser import ConfigParser, ConfigError
from npm_fetcher import NPMFetcher, NPMFetcherError
from dependency_graph import DependencyGraph
from test_repository_loader import TestRepositoryLoader, TestRepositoryError
from d2_generator import D2Generator
from ascii_tree import ASCIITreeGenerator


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
        print()
        
        package_name = config['package_name']
        package_version = config['package_version']
        filter_substring = config.get('filter_substring', '')
        test_mode = config.get('test_mode', False)
        
        # Этап 3: Построение графа зависимостей
        print("=" * 60)
        print("Построение графа зависимостей...")
        print("=" * 60)
        
        graph = DependencyGraph(filter_substring=filter_substring)
        
        try:
            if test_mode:
                # Режим тестирования
                test_repo_path = config.get('test_repository_path', '')
                if not test_repo_path:
                    print("Ошибка: в режиме тестирования необходимо указать test_repository_path", file=sys.stderr)
                    return 1
                
                loader = TestRepositoryLoader(test_repo_path)
                get_deps_func = loader.create_dependency_getter()
                
                print(f"\nЗагрузка тестового репозитория из: {test_repo_path}")
                print(f"Анализ пакета: {package_name}")
                
            else:
                # Режим работы с npm registry
                registry_url = config['repository_url']
                fetcher = NPMFetcher(registry_url)
                
                def get_deps_func(pkg: str) -> dict:
                    """Обертка для получения зависимостей через fetcher."""
                    return fetcher.get_dependencies(pkg, "latest")
                
                print(f"\nПолучение зависимостей из npm registry...")
                print(f"Пакет: {package_name} (версия: {package_version})")
            
            # Построение графа с использованием DFS
            print("\nПостроение графа зависимостей (DFS)...")
            
            # Сначала строим граф от заданного пакета
            graph.build_graph_dfs(package_name, get_deps_func)
            
            # В тестовом режиме строим полный граф для корректного поиска обратных зависимостей
            if test_mode:
                # Получаем все пакеты из тестового репозитория
                if hasattr(loader, 'repository'):
                    all_test_packages = set(loader.repository.keys())
                    # Строим граф от каждого пакета, который еще не обработан
                    for pkg in all_test_packages:
                        if pkg not in graph.get_all_packages():
                            graph.build_graph_dfs(pkg, get_deps_func)
            
            # Вывод результатов
            print("\n" + "=" * 60)
            print("Результаты анализа:")
            print("=" * 60)
            
            # Прямые зависимости
            direct_deps = graph.get_direct_dependencies(package_name)
            print(f"\nПрямые зависимости '{package_name}': {len(direct_deps)}")
            if direct_deps:
                for dep in sorted(direct_deps):
                    print(f"  - {dep}")
            else:
                print("  (нет прямых зависимостей)")
            
            # Все зависимости (транзитивные)
            all_deps = graph.get_all_dependencies(package_name)
            print(f"\nВсе зависимости '{package_name}' (транзитивные): {len(all_deps)}")
            if all_deps:
                for dep in sorted(all_deps):
                    print(f"  - {dep}")
            
            # Циклические зависимости
            cycles = graph.get_cycles()
            if cycles:
                print(f"\n⚠ Обнаружены циклические зависимости: {len(cycles)}")
                for i, cycle in enumerate(cycles, 1):
                    cycle_str = " -> ".join(cycle)
                    print(f"  Цикл {i}: {cycle_str}")
            else:
                print("\n✓ Циклических зависимостей не обнаружено")
            
            # Обратные зависимости (Этап 4)
            reverse_deps = graph.get_reverse_dependencies(package_name)
            print(f"\nОбратные зависимости '{package_name}' (пакеты, которые зависят от него): {len(reverse_deps)}")
            if reverse_deps:
                for dep in sorted(reverse_deps):
                    print(f"  - {dep}")
            else:
                print("  (нет обратных зависимостей)")
            
            # Статистика
            all_packages = graph.get_all_packages()
            print(f"\nВсего уникальных пакетов в графе: {len(all_packages)}")
            
            if filter_substring:
                print(f"\nПрименена фильтрация по подстроке: '{filter_substring}'")
            
            # Этап 5: Визуализация
            print("\n" + "=" * 60)
            print("Визуализация графа зависимостей")
            print("=" * 60)
            
            # Генерация D2 диаграммы
            d2_gen = D2Generator(graph, package_name)
            d2_diagram = d2_gen.generate()
            
            print("\nОписание графа на языке D2:")
            print("-" * 60)
            print(d2_diagram)
            print("-" * 60)
            
            # Генерация ASCII-дерева (если включен режим)
            if config.get('ascii_tree_mode', False):
                print("\nASCII-дерево зависимостей:")
                print("-" * 60)
                ascii_gen = ASCIITreeGenerator(graph, package_name)
                ascii_tree = ascii_gen.generate_compact()
                print(ascii_tree)
                print("-" * 60)
            
        except TestRepositoryError as e:
            print(f"Ошибка тестового репозитория: {e}", file=sys.stderr)
            return 1
        except NPMFetcherError as e:
            print(f"Ошибка получения зависимостей: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Ошибка построения графа: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        
        return 0
        
    except ConfigError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

