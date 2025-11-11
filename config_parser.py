"""
Модуль для парсинга и валидации конфигурационного файла.
"""
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigError(Exception):
    """Исключение для ошибок конфигурации."""
    pass


class ConfigParser:
    """Класс для парсинга и валидации конфигурации."""
    
    REQUIRED_PARAMS = [
        'package_name',
        'repository_url',
        'test_mode',
        'package_version',
        'ascii_tree_mode',
        'filter_substring'
    ]
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Инициализация парсера конфигурации.
        
        Args:
            config_path: Путь к конфигурационному файлу
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
    
    def load_config(self) -> Dict[str, Any]:
        """
        Загружает и валидирует конфигурацию из файла.
        
        Returns:
            Словарь с параметрами конфигурации
            
        Raises:
            ConfigError: При ошибках загрузки или валидации
        """
        # Проверка существования файла
        if not os.path.exists(self.config_path):
            raise ConfigError(f"Конфигурационный файл не найден: {self.config_path}")
        
        # Загрузка YAML
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Ошибка парсинга YAML: {e}")
        except Exception as e:
            raise ConfigError(f"Ошибка чтения файла: {e}")
        
        # Проверка на пустую конфигурацию
        if not self.config:
            raise ConfigError("Конфигурационный файл пуст")
        
        # Валидация параметров
        self._validate_config()
        
        return self.config
    
    def _validate_config(self) -> None:
        """
        Валидирует все параметры конфигурации.
        
        Raises:
            ConfigError: При ошибках валидации
        """
        # Проверка наличия обязательных параметров
        missing_params = []
        for param in self.REQUIRED_PARAMS:
            if param not in self.config:
                missing_params.append(param)
        
        if missing_params:
            raise ConfigError(
                f"Отсутствуют обязательные параметры: {', '.join(missing_params)}"
            )
        
        # Валидация package_name
        package_name = self.config.get('package_name')
        if not isinstance(package_name, str) or not package_name.strip():
            raise ConfigError("Параметр 'package_name' должен быть непустой строкой")
        
        # Валидация repository_url
        repository_url = self.config.get('repository_url')
        if not isinstance(repository_url, str) or not repository_url.strip():
            raise ConfigError("Параметр 'repository_url' должен быть непустой строкой")
        
        # Валидация test_mode
        test_mode = self.config.get('test_mode')
        if not isinstance(test_mode, bool):
            raise ConfigError("Параметр 'test_mode' должен быть булевым значением (true/false)")
        
        # Валидация test_repository_path (если test_mode = true)
        if test_mode:
            test_repository_path = self.config.get('test_repository_path', '')
            if not isinstance(test_repository_path, str):
                raise ConfigError("Параметр 'test_repository_path' должен быть строкой")
            if test_repository_path and not os.path.exists(test_repository_path):
                raise ConfigError(
                    f"Файл тестового репозитория не найден: {test_repository_path}"
                )
        
        # Валидация package_version
        package_version = self.config.get('package_version')
        if not isinstance(package_version, str) or not package_version.strip():
            raise ConfigError("Параметр 'package_version' должен быть непустой строкой")
        
        # Валидация ascii_tree_mode
        ascii_tree_mode = self.config.get('ascii_tree_mode')
        if not isinstance(ascii_tree_mode, bool):
            raise ConfigError(
                "Параметр 'ascii_tree_mode' должен быть булевым значением (true/false)"
            )
        
        # Валидация filter_substring
        filter_substring = self.config.get('filter_substring')
        if not isinstance(filter_substring, str):
            raise ConfigError("Параметр 'filter_substring' должен быть строкой")
        
        # Нормализация значений
        self.config['package_name'] = package_name.strip()
        self.config['repository_url'] = repository_url.strip()
        self.config['package_version'] = package_version.strip()
        self.config['filter_substring'] = filter_substring.strip() if filter_substring else ""
    
    def get_config(self) -> Dict[str, Any]:
        """
        Возвращает загруженную конфигурацию.
        
        Returns:
            Словарь с параметрами конфигурации
        """
        return self.config.copy()

