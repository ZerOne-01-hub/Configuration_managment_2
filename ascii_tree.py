"""
Модуль для генерации ASCII-дерева зависимостей.
"""
from typing import Dict, Set, List, Optional
from dependency_graph import DependencyGraph


class ASCIITreeGenerator:
    """Класс для генерации ASCII-дерева зависимостей."""
    
    def __init__(self, graph: DependencyGraph, root_package: str):
        """
        Инициализация генератора ASCII-дерева.
        
        Args:
            graph: Граф зависимостей
            root_package: Корневой пакет для визуализации
        """
        self.graph = graph
        self.root_package = root_package
        self.visited = set()
    
    def generate(self) -> str:
        """
        Генерирует ASCII-дерево зависимостей.
        
        Returns:
            Строка с ASCII-деревом
        """
        lines = []
        lines.append(f"Зависимости пакета: {self.root_package}")
        lines.append("=" * 60)
        lines.append("")
        
        if self.root_package not in self.graph.get_all_packages():
            lines.append("(нет зависимостей)")
            return "\n".join(lines)
        
        self.visited.clear()
        self._build_tree(self.root_package, "", True, lines, set())
        
        return "\n".join(lines)
    
    def _build_tree(
        self,
        package: str,
        prefix: str,
        is_last: bool,
        lines: List[str],
        path: Set[str]
    ) -> None:
        """
        Рекурсивно строит дерево зависимостей.
        
        Args:
            package: Текущий пакет
            prefix: Префикс для отступов
            is_last: Является ли пакет последним в списке
            lines: Список строк для вывода
            path: Путь от корня (для обнаружения циклов)
        """
        # Обнаружение циклов
        if package in path:
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{package} [ЦИКЛ]")
            return
        
        # Добавляем пакет в путь
        path.add(package)
        
        # Получаем зависимости
        deps = sorted(self.graph.get_direct_dependencies(package))
        
        # Выводим текущий пакет
        if package == self.root_package:
            lines.append(f"{package}")
        else:
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{package}")
        
        # Обрабатываем зависимости
        if deps:
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            for i, dep in enumerate(deps):
                is_last_dep = (i == len(deps) - 1)
                self._build_tree(dep, new_prefix, is_last_dep, lines, path.copy())
        
        # Удаляем пакет из пути после обработки
        path.discard(package)
    
    def generate_compact(self) -> str:
        """
        Генерирует компактное ASCII-дерево (без повторений).
        
        Returns:
            Строка с компактным ASCII-деревом
        """
        lines = []
        lines.append(f"Зависимости пакета: {self.root_package} (компактное представление)")
        lines.append("=" * 60)
        lines.append("")
        
        if self.root_package not in self.graph.get_all_packages():
            lines.append("(нет зависимостей)")
            return "\n".join(lines)
        
        self.visited.clear()
        self._build_tree_compact(self.root_package, "", True, lines)
        
        return "\n".join(lines)
    
    def _build_tree_compact(
        self,
        package: str,
        prefix: str,
        is_last: bool,
        lines: List[str]
    ) -> None:
        """
        Рекурсивно строит компактное дерево зависимостей (без повторений).
        
        Args:
            package: Текущий пакет
            prefix: Префикс для отступов
            is_last: Является ли пакет последним в списке
            lines: Список строк для вывода
        """
        # Пропускаем уже посещенные пакеты (кроме корневого)
        if package != self.root_package and package in self.visited:
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{package} [уже показано выше]")
            return
        
        self.visited.add(package)
        
        # Получаем зависимости
        deps = sorted(self.graph.get_direct_dependencies(package))
        
        # Выводим текущий пакет
        if package == self.root_package:
            lines.append(f"{package}")
        else:
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{package}")
        
        # Обрабатываем зависимости
        if deps:
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            for i, dep in enumerate(deps):
                is_last_dep = (i == len(deps) - 1)
                self._build_tree_compact(dep, new_prefix, is_last_dep, lines)

