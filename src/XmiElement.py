from __future__ import annotations

from typing import (
    Literal,
    overload
)
from xml.etree import ElementTree as ET

from src.Config import Config
from src.exceptions import (
    NoAttribute,
    NoElement
)


class XmiElement():
    namespaces = [Config.uml_namespace, Config.xmi_namespace]

    def __init__(self, element: ET.Element):
        self._element = element

    @property
    def syganture(self) -> tuple[str, str]:
        return self.get("id"), self.get("name")

    def get(self, key: str, force_namespace: bool = False) -> str:
        for namespace in ([""] if not force_namespace else []) + self.namespaces:
            if (attribute := self._element.get(f"{namespace}{key}")) is not None:
                return attribute
        raise NoAttribute()

    @overload
    def find(self, name: str, all: Literal[False] = False, force_namespace: bool = False) -> XmiElement: ...

    @overload
    def find(self, name: str, all: Literal[True], force_namespace: bool = False) -> list[XmiElement]: ...

    def find(self, name: str, all: bool = False, force_namespace: bool = False) -> XmiElement | list[XmiElement]:
        find_func = self._element.findall if all else self._element.find
        for namespace in ([""] if not force_namespace else []) + self.namespaces:
            if (result := find_func(f"{namespace}{name}")) is not None:
                return list(map(XmiElement, result)) if all else XmiElement(result)  # type: ignore
        raise NoElement()
