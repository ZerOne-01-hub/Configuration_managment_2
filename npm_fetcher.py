"""
Модуль для получения информации о пакетах из npm registry.
Использует только стандартные библиотеки Python без менеджеров пакетов.
"""
import urllib.request
import urllib.error
import ssl
import json
from typing import Dict, Any, Optional, List


class NPMFetcherError(Exception):
    """Исключение для ошибок получения данных из npm registry."""
    pass


class NPMFetcher:
    """Класс для получения информации о пакетах из npm registry."""
    
    def __init__(self, registry_url: str = "https://registry.npmjs.org"):
        """
        Инициализация fetcher.
        
        Args:
            registry_url: URL npm registry
        """
        self.registry_url = registry_url.rstrip('/')
    
    def _make_request(self, url: str) -> Dict[str, Any]:
        """
        Выполняет HTTP GET запрос к указанному URL.
        
        Args:
            url: URL для запроса
            
        Returns:
            Распарсенный JSON ответ
            
        Raises:
            NPMFetcherError: При ошибках запроса или парсинга
        """
        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            
            # Создаем SSL контекст для работы с HTTPS
            # Используем unverified context для совместимости с различными системами
            # В продакшене следует использовать проверенные сертификаты
            ssl_context = ssl._create_unverified_context()
            
            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                if response.status != 200:
                    raise NPMFetcherError(
                        f"HTTP ошибка {response.status}: {response.reason}"
                    )
                
                data = response.read().decode('utf-8')
                return json.loads(data)
                
        except urllib.error.URLError as e:
            raise NPMFetcherError(f"Ошибка сети: {e}")
        except json.JSONDecodeError as e:
            raise NPMFetcherError(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise NPMFetcherError(f"Неожиданная ошибка: {e}")
    
    def _resolve_version(self, package_name: str, version: str) -> str:
        """
        Разрешает версию пакета (например, 'latest' -> конкретная версия).
        
        Args:
            package_name: Имя пакета
            version: Версия или тег (например, 'latest')
            
        Returns:
            Конкретная версия пакета
        """
        if version == "latest":
            # Получаем информацию о пакете для определения latest версии
            url = f"{self.registry_url}/{package_name}"
            package_info = self._make_request(url)
            
            if 'dist-tags' in package_info and 'latest' in package_info['dist-tags']:
                return package_info['dist-tags']['latest']
            elif 'versions' in package_info:
                # Если нет dist-tags, берем последнюю версию из списка
                versions = sorted(package_info['versions'].keys(), reverse=True)
                if versions:
                    return versions[0]
            
            raise NPMFetcherError(f"Не удалось определить latest версию для {package_name}")
        
        return version
    
    def get_package_info(self, package_name: str, version: str = "latest") -> Dict[str, Any]:
        """
        Получает информацию о пакете для указанной версии.
        
        Args:
            package_name: Имя пакета
            version: Версия пакета (по умолчанию 'latest')
            
        Returns:
            Словарь с информацией о пакете
            
        Raises:
            NPMFetcherError: При ошибках получения данных
        """
        try:
            # Разрешаем версию
            resolved_version = self._resolve_version(package_name, version)
            
            # Получаем информацию о конкретной версии
            url = f"{self.registry_url}/{package_name}/{resolved_version}"
            package_info = self._make_request(url)
            
            return package_info
            
        except NPMFetcherError:
            raise
        except Exception as e:
            raise NPMFetcherError(f"Ошибка получения информации о пакете: {e}")
    
    def get_dependencies(self, package_name: str, version: str = "latest") -> Dict[str, str]:
        """
        Получает прямые зависимости пакета.
        
        Args:
            package_name: Имя пакета
            version: Версия пакета (по умолчанию 'latest')
            
        Returns:
            Словарь зависимостей в формате {имя: версия}
            
        Raises:
            NPMFetcherError: При ошибках получения данных
        """
        package_info = self.get_package_info(package_name, version)
        
        # Извлекаем зависимости из package.json
        dependencies = package_info.get('dependencies', {})
        
        return dependencies

