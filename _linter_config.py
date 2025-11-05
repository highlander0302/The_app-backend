"""HHow about module docstringHow about module docstringHow about module docstringHow about module docstringHow about module docstringHow about module docstringHow about module docstringow about module docstring"""

from abc import ABC, abstractmethod


class TestInterface(ABC):
    """This interface is for testing."""

    @abstractmethod
    def conform_to_me(self, message: str) -> str:
        """THis is the function that returns hallow word with typo"""


class BatConcreteClass(TestInterface):
    """This is a concrete implementation of the testing class"""

    def conform_to_me(self, message: str) -> str:
        return "hallow"

    def _helper(self, x: int, y: int) -> int:
        return x * y
