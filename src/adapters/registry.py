"""
Adapter registry for managing and retrieving data source adapters.
"""

from datetime import timedelta
from typing import Optional

from src.adapters.base import SourceAdapter


class AdapterRegistry:
    """
    Singleton registry for managing all data source adapters.
    
    Provides methods to retrieve adapters by name, list all available adapters,
    and get polling intervals for each source.
    """
    
    _instance: Optional["AdapterRegistry"] = None
    _adapters: dict[str, SourceAdapter] = {}
    
    def __new__(cls) -> "AdapterRegistry":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._adapters = {}
        return cls._instance
    
    def register(self, adapter: SourceAdapter) -> None:
        """
        Register an adapter with the registry.
        
        Args:
            adapter: Adapter instance to register.
        """
        self._adapters[adapter.source_name] = adapter
    
    def get_adapter(self, source: str) -> SourceAdapter:
        """
        Get an adapter by source name.
        
        Args:
            source: Source name (e.g., 'gdelt', 'acled', 'imf')
            
        Returns:
            The adapter instance for the specified source.
            
        Raises:
            KeyError: If the source is not registered.
        """
        if source not in self._adapters:
            raise KeyError(f"No adapter registered for source: {source}")
        return self._adapters[source]
    
    def list_adapters(self) -> list[str]:
        """
        List all registered adapter source names.
        
        Returns:
            List of source names.
        """
        return list(self._adapters.keys())
    
    def get_poll_interval(self, source: str) -> timedelta:
        """
        Get the polling interval for a source.
        
        Args:
            source: Source name.
            
        Returns:
            Polling interval as timedelta.
            
        Raises:
            KeyError: If the source is not registered.
        """
        adapter = self.get_adapter(source)
        return adapter.poll_interval
    
    def clear(self) -> None:
        """Clear all registered adapters (primarily for testing)."""
        self._adapters.clear()
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (primarily for testing)."""
        cls._instance = None
        cls._adapters = {}


# Export the registry
__all__ = ["AdapterRegistry", "SourceAdapter"]