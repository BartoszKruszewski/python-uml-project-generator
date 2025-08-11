from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum


class ParameterDirection(Enum):
    IN = "in"
    RETURN = "return"


@dataclass
class AbstractSyntax(ABC):
    id: str
    name: str


@dataclass
class DataType(AbstractSyntax):
    pass


@dataclass
class Property(AbstractSyntax):
    type: str


@dataclass
class Parameter(AbstractSyntax):
    type: str
    direction: ParameterDirection


@dataclass
class Operation(AbstractSyntax):
    parameters: list[Parameter]


@dataclass
class Class(AbstractSyntax):
    properties: list[Property]
    operations: list[Operation]


@dataclass
class Dependency(AbstractSyntax):
    client: str
    supplier: str


@dataclass
class Package(AbstractSyntax):
    subpackages: list[Package]
    classes: list[Class]
    dependencies: list[Dependency]
    data_types: list[DataType]


@dataclass
class Project(AbstractSyntax):
    packages: list[Package]
