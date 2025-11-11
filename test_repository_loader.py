"""
Модуль для загрузки тестовых репозиториев из файла.
В тестовом режиме пакеты называются большими латинскими буквами.
"""
import json
import os
from typing import Dict, Callable


class TestRepositoryError(Exception):
    """Исключение для ошибок работы с тестовым репозиторием."""
    pass


class TestRepositoryLoader:
    """Класс для загрузки и работы с тестовым репозиторием."""
    
    def __init__(self, file_path: str):
        """
        Инициализация загрузчика тестового репозитория.
        
        Args:
            file_path: Путь к файлу тестового репозитория
        """
        self.file_path = file_path
        self.repository: Dict[str, Dict[str, str]] = {}
        self._load_repository()
    
    def _load_repository(self) -> None:
        """Загружает тестовый репозиторий из файла."""
        if not os.path.exists(self.file_path):
            raise TestRepositoryError(f"Файл тестового репозитория не найден: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Пытаемся загрузить как JSON
                try:
                    self.repository = json.loads(content)
                except json.JSONDecodeError:
                    # Если не JSON, пытаемся загрузить как текстовый формат
                    self.repository = self._parse_text_format(content)
        
        except Exception as e:
            raise TestRepositoryError(f"Ошибка чтения файла: {e}")
    
    def _parse_text_format(self, content: str) -> Dict[str, Dict[str, str]]:
        """
        Парсит текстовый формат репозитория.
        Формат: PACKAGE: DEP1, DEP2, DEP3
        
        Args:
            content: Содержимое файла
            
        Returns:
            Словарь репозитория
        """
        repository = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Формат: PACKAGE: DEP1, DEP2, DEP3
            if ':' in line:
                parts = line.split(':', 1)
                package = parts[0].strip()
                deps_str = parts[1].strip() if len(parts) > 1 else ""
                
                # Парсим зависимости
                dependencies = {}
                if deps_str:
                    for dep in deps_str.split(','):
                        dep = dep.strip()
                        if dep:
                            # Формат может быть "DEP" или "DEP@VERSION"
                            if '@' in dep:
                                dep_name, dep_version = dep.split('@', 1)
                                dependencies[dep_name.strip()] = dep_version.strip()
                            else:
                                dependencies[dep] = "1.0.0"  # Версия по умолчанию
                
                repository[package] = dependencies
        
        return repository
    
    def get_dependencies(self, package_name: str, version: str = "latest") -> Dict[str, str]:
        """
        Получает зависимости пакета из тестового репозитория.
        
        Args:
            package_name: Имя пакета (большие латинские буквы)
            version: Версия пакета (игнорируется в тестовом режиме)
            
        Returns:
            Словарь зависимостей
        """
        if package_name not in self.repository:
            return {}
        
        return self.repository[package_name].copy()
    
    def create_dependency_getter(self) -> Callable[[str], Dict[str, str]]:
        """
        Создает функцию для получения зависимостей, совместимую с DependencyGraph.
        
        Returns:
            Функция для получения зависимостей пакета
        """
        def get_deps(package_name: str) -> Dict[str, str]:
            return self.get_dependencies(package_name)
        
        return get_deps

