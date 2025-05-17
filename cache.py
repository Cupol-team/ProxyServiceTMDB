import time
import asyncio
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

class SimpleCache:
    """
    кэш в памяти со временем жизни 
    """
    
    def __init__(self, ttl_seconds: int = 300, cleanup_interval: int = 60):
        """
        Инициализация кэша
        
        Args:
            ttl_seconds: Время жизни кэша в секундах (по умолчанию 5 минут)
            cleanup_interval: Интервал автоматической очистки кэша в секундах (по умолчанию 1 минута)
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = cleanup_interval
        self.cleanup_task = None
    
    async def start_cleanup_task(self):
        """Запускает задачу периодической очистки кэша"""
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Периодически очищает устаревшие записи в кэше"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception:
                pass
    
    def _cleanup_expired(self):
        """Удаляет устаревшие записи из кэша"""
        now = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self.cache.items():
            if now - timestamp > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получение значения из кэша
        
        Args:
            key: Ключ для поиска в кэше
            
        Returns:
            Значение из кэша или None, если ключ не найден или истекло время жизни
        """
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        if time.time() - timestamp > self.ttl_seconds:
            del self.cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Сохранение значения в кэше
        
        Args:
            key: Ключ для сохранения
            value: Значение для сохранения
        """
        self.cache[key] = (value, time.time())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики кэша
        
        Returns:
            Словарь со статистикой кэша
        """
        now = time.time()
        active_items = 0
        
        for _, timestamp in self.cache.values():
            if now - timestamp <= self.ttl_seconds:
                active_items += 1
        
        return {
            "total_size": len(self.cache),
            "active_items": active_items,
            "ttl_seconds": self.ttl_seconds,
            "cleanup_interval": self.cleanup_interval,
            "next_cleanup_in": self.cleanup_interval - (int(time.time()) % self.cleanup_interval),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

cache = SimpleCache() 