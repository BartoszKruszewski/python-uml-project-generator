from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum


class ParameterDirection(Enum):
    """Enum representing the direction of a parameter."""

    IN = "in"
    RETURN = "return"


class RelationType(Enum):
    """Enum representing the type of a relation."""

    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    DEPENDENCY = "dependency"
    REALIZATION = "realization"
    GENERALIZATION = "generalization"


@dataclass
class AbstractSyntax(ABC):
    """Abstract base class for all syntax elements."""
    id: str
    name: str


@dataclass
class DataType(AbstractSyntax):
    """Data type syntax element."""


@dataclass
class Property(AbstractSyntax):
    """Property syntax element."""
    type: str


@dataclass
class Parameter(AbstractSyntax):
    """Parameter syntax element."""
    type: str
    direction: ParameterDirection


@dataclass
class Operation(AbstractSyntax):
    """Operation syntax element."""
    parameters: list[Parameter]


@dataclass
class Class(AbstractSyntax):
    """Class syntax element."""
    properties: list[Property]
    operations: list[Operation]


@dataclass
class Relation(AbstractSyntax):
    """Relation syntax element."""
    type: RelationType
    client: str
    supplier: str


@dataclass
class Package(AbstractSyntax):
    """Package syntax element."""
    subpackages: list[Package]
    classes: list[Class]
    dependencies: list[Relation]
    data_types: list[DataType]


@dataclass
class Project(AbstractSyntax):
    """Project syntax element."""
    packages: list[Package]
