from __future__ import annotations

from typing import (
    Literal,
    overload
)
from xml.etree import ElementTree as ET

from project_generator.Config import Config
from project_generator.exceptions import (
    NoAttribute,
    NoElement
)


class XmiElement:
    """XMI element wrapper for easier attribute and child element access."""

    namespaces = [Config.uml_namespace, Config.xmi_namespace]

    def __init__(self, element: ET.Element):
        """
        Args:
            element: ET.Element to wrap.
        """
        self._element = element

    @property
    def syganture(self) -> tuple[str, str]:
        """Gets sygnature of the element.

        Returns:
            Sygnature of the element as a tuple of (id, name).
        """
        return self.get("id"), self.get("name")

    def get(self, key: str, force_namespace: bool = False) -> str:
        """Gets the attribute value for the given key.

        Args:
            key: Key of the attribute to get.
            force_namespace: Force searching with namespaces.
        Returns:
            Attribute value.
        """
        for namespace in ([""] if not force_namespace else []) + self.namespaces:
            if (attribute := self._element.get(f"{namespace}{key}")) is not None:
                return attribute
        raise NoAttribute(f"Attribute {key} not found in element {self._element.tag}.")

    @overload
    def find(self, name: str, all: Literal[False] = False, force_namespace: bool = False) -> XmiElement: ...

    @overload
    def find(self, name: str, all: Literal[True], force_namespace: bool = False) -> list[XmiElement]: ...

    def find(self, name: str, all: bool = False, force_namespace: bool = False) -> XmiElement | list[XmiElement]:
        """Finds child element(s) by name.

        Args:
            name: Name of the child element to find.
            all: Determine whether to find all matching elements or just the first one.
            force_namespace: Force searching with namespaces.
        Returns:
            Found child element(s).
        """
        find_func = self._element.findall if all else self._element.find
        for namespace in ([""] if not force_namespace else []) + self.namespaces:
            if (result := find_func(f"{namespace}{name}")) is not None:
                return list(map(XmiElement, result)) if all else XmiElement(result)  # type: ignore
        raise NoElement(f"Element {name} not found in element {self._element.tag}.")
