"""
Модуль для построения графа зависимостей с использованием DFS алгоритма.
"""
from typing import Dict, Set, List, Optional
from collections import defaultdict


class DependencyGraphError(Exception):
    """Исключение для ошибок работы с графом зависимостей."""
    pass


class DependencyGraph:
    """Класс для представления и работы с графом зависимостей."""
    
    def __init__(self, filter_substring: str = ""):
        """
        Инициализация графа зависимостей.
        
        Args:
            filter_substring: Подстрока для фильтрации пакетов
        """
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.filter_substring = filter_substring.lower() if filter_substring else ""
        self.visited: Set[str] = set()
        self.recursion_stack: Set[str] = set()
        self.cycles: List[List[str]] = []
    
    def _should_filter(self, package_name: str) -> bool:
        """
        Проверяет, нужно ли фильтровать пакет.
        
        Args:
            package_name: Имя пакета
            
        Returns:
            True если пакет должен быть отфильтрован
        """
        if not self.filter_substring:
            return False
        return self.filter_substring in package_name.lower()
    
    def add_dependency(self, package: str, dependency: str) -> None:
        """
        Добавляет зависимость в граф.
        
        Args:
            package: Имя пакета
            dependency: Имя зависимости
        """
        # Пропускаем отфильтрованные пакеты
        if self._should_filter(package) or self._should_filter(dependency):
            return
        
        self.graph[package].add(dependency)
        # Убеждаемся, что зависимость тоже есть в графе (даже если у неё нет зависимостей)
        if dependency not in self.graph:
            self.graph[dependency] = set()
    
    def build_graph_dfs(
        self,
        package: str,
        get_dependencies_func,
        visited: Optional[Set[str]] = None,
        path: Optional[List[str]] = None
    ) -> None:
        """
        Строит граф зависимостей используя алгоритм DFS с рекурсией.
        
        Args:
            package: Имя пакета для обработки
            get_dependencies_func: Функция для получения зависимостей пакета
            visited: Множество посещенных пакетов (для предотвращения повторной обработки)
            path: Текущий путь обхода (для обнаружения циклов)
        """
        if visited is None:
            visited = set()
        if path is None:
            path = []
        
        # Пропускаем отфильтрованные пакеты
        if self._should_filter(package):
            return
        
        # Обнаружение циклических зависимостей
        if package in path:
            cycle_start = path.index(package)
            cycle = path[cycle_start:] + [package]
            self.cycles.append(cycle)
            return
        
        # Если пакет уже обработан, не обрабатываем его снова
        if package in visited:
            return
        
        # Добавляем пакет в посещенные и в текущий путь
        visited.add(package)
        path.append(package)
        
        try:
            # Получаем зависимости пакета
            dependencies = get_dependencies_func(package)
            
            # Обрабатываем каждую зависимость рекурсивно
            for dep_name in dependencies.keys():
                if not self._should_filter(dep_name):
                    self.add_dependency(package, dep_name)
                    self.build_graph_dfs(dep_name, get_dependencies_func, visited, path.copy())
        
        except Exception as e:
            # Если не удалось получить зависимости, просто пропускаем
            # и продолжаем работу с другими пакетами
            pass
        
        # Удаляем пакет из текущего пути после обработки
        if path and path[-1] == package:
            path.pop()
    
    def get_all_dependencies(self, package: str) -> Set[str]:
        """
        Получает все зависимости пакета (транзитивные).
        
        Args:
            package: Имя пакета
            
        Returns:
            Множество всех зависимостей
        """
        if package not in self.graph:
            return set()
        
        all_deps = set()
        visited = set()
        
        def collect_deps(pkg: str):
            if pkg in visited or self._should_filter(pkg):
                return
            visited.add(pkg)
            for dep in self.graph.get(pkg, set()):
                if not self._should_filter(dep):
                    all_deps.add(dep)
                    collect_deps(dep)
        
        collect_deps(package)
        return all_deps
    
    def get_direct_dependencies(self, package: str) -> Set[str]:
        """
        Получает прямые зависимости пакета.
        
        Args:
            package: Имя пакета
            
        Returns:
            Множество прямых зависимостей
        """
        return self.graph.get(package, set())
    
    def get_cycles(self) -> List[List[str]]:
        """
        Возвращает список обнаруженных циклов.
        
        Returns:
            Список циклов, где каждый цикл представлен списком пакетов
        """
        return self.cycles
    
    def has_cycles(self) -> bool:
        """
        Проверяет наличие циклов в графе.
        
        Returns:
            True если есть циклы
        """
        return len(self.cycles) > 0
    
    def get_all_packages(self) -> Set[str]:
        """
        Возвращает все пакеты в графе.
        
        Returns:
            Множество всех пакетов
        """
        all_packages = set(self.graph.keys())
        for deps in self.graph.values():
            all_packages.update(deps)
        return all_packages
    
    def clear(self) -> None:
        """Очищает граф."""
        self.graph.clear()
        self.visited.clear()
        self.recursion_stack.clear()
        self.cycles.clear()

