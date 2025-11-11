"""
Модуль для генерации диаграмм D2 из графа зависимостей.
"""
from typing import Dict, Set
from dependency_graph import DependencyGraph


class D2Generator:
    """Класс для генерации D2 диаграмм."""
    
    def __init__(self, graph: DependencyGraph, root_package: str):
        """
        Инициализация генератора D2.
        
        Args:
            graph: Граф зависимостей
            root_package: Корневой пакет для визуализации
        """
        self.graph = graph
        self.root_package = root_package
    
    def generate(self) -> str:
        """
        Генерирует описание графа на языке D2.
        
        Returns:
            Строка с описанием графа на языке D2
        """
        lines = []
        lines.append("# Граф зависимостей пакета")
        lines.append(f"# Корневой пакет: {self.root_package}")
        lines.append("")
        
        # Получаем все пакеты в графе
        all_packages = self.graph.get_all_packages()
        
        # Добавляем все узлы
        for pkg in sorted(all_packages):
            # Выделяем корневой пакет
            if pkg == self.root_package:
                lines.append(f'"{pkg}": {{')
                lines.append('  style.fill: "#e1f5ff"')
                lines.append('  style.stroke: "#01579b"')
                lines.append('  style.stroke-width: 3')
                lines.append("}")
            else:
                lines.append(f'"{pkg}"')
        
        lines.append("")
        
        # Добавляем все связи
        visited_edges = set()
        for pkg in sorted(all_packages):
            deps = self.graph.get_direct_dependencies(pkg)
            for dep in sorted(deps):
                edge = (pkg, dep)
                if edge not in visited_edges:
                    # Выделяем прямые зависимости корневого пакета
                    if pkg == self.root_package:
                        lines.append(f'"{pkg}" -> "{dep}": {{')
                        lines.append('  style.stroke: "#0277bd"')
                        lines.append('  style.stroke-width: 2')
                        lines.append("}")
                    else:
                        lines.append(f'"{pkg}" -> "{dep}"')
                    visited_edges.add(edge)
        
        # Добавляем информацию о циклах
        cycles = self.graph.get_cycles()
        if cycles:
            lines.append("")
            lines.append("# Циклические зависимости")
            for i, cycle in enumerate(cycles, 1):
                if len(cycle) > 1:
                    # Создаем связи для цикла с выделением
                    for j in range(len(cycle) - 1):
                        from_node = cycle[j]
                        to_node = cycle[j + 1]
                        edge = (from_node, to_node)
                        if edge in visited_edges:
                            # Обновляем существующую связь
                            lines.append(f'"{from_node}" -> "{to_node}": {{')
                            lines.append('  style.stroke: "#d32f2f"')
                            lines.append('  style.stroke-width: 2')
                            lines.append('  style.stroke-dash: 3')
                            lines.append("}")
        
        return "\n".join(lines)

