"""Base tool interface for external integrations"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """Base interface for all external tools"""
    
    @abstractmethod
    def name(self) -> str:
        """Return the tool name"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool's parameter schema"""
        pass