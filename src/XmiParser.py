from pathlib import Path
from typing import (
    Callable,
    TypeVar
)
from xml.etree import ElementTree as ET

from src.syntax import (
    AbstractSyntax,
    Class,
    DataType,
    Dependency,
    Operation,
    Package,
    Parameter,
    ParameterDirection,
    Project,
    Property
)
from src.XmiElement import XmiElement


class XmiParser:
    T = TypeVar("T", bound="AbstractSyntax")

    @classmethod
    def parse(cls, xmi_path: Path) -> Project:
        tree = ET.parse(xmi_path)
        root = XmiElement(tree.getroot())
        model = root.find("Model")

        return Project(
            *model.syganture,
            cls._parse_all(model, "packagedElement", "uml:Package", cls._parse_package)
        )

    @classmethod
    def _parse_all(
        cls,
        parent: XmiElement,
        element_name: str,
        uml_type: str,
        parser: Callable[[XmiElement], T]
    ) -> list[T]:
        return [
            parser(element)
            for element in parent.find(element_name, True)
            if element.get("type", True) == uml_type
        ]

    @classmethod
    def _parse_package(cls, package_element: XmiElement) -> Package:
        return Package(
            *package_element.syganture,
            cls._parse_all(package_element, "packagedElement", "uml:Class", cls._parse_class),
            cls._parse_all(package_element, "packagedElement", "uml:Dependency", cls._parse_dependency),
            cls._parse_all(package_element, "packagedElement", "uml:DataType", cls._parse_data_type),
        )

    @classmethod
    def _parse_dependency(cls, dependency_element: XmiElement) -> Dependency:
        return Dependency(
            *dependency_element.syganture,
            dependency_element.get("client"),
            dependency_element.get("supplier")
        )

    @classmethod
    def _parse_data_type(cls, data_type_element: XmiElement) -> DataType:
        return DataType(*data_type_element.syganture)

    @classmethod
    def _parse_class(cls, class_element: XmiElement) -> Class:
        return Class(
            *class_element.syganture,
            cls._parse_all(class_element, "ownedAttribute", "uml:Property", cls._parse_property),
            cls._parse_all(class_element, "ownedOperation", "uml:Operation", cls._parse_operation)
        )

    @classmethod
    def _parse_property(cls, property_element: XmiElement) -> Property:
        return Property(*property_element.syganture, property_element.get("type"))

    @classmethod
    def _parse_operation(cls, operation_element: XmiElement) -> Operation:
        return Operation(
            *operation_element.syganture,
            cls._parse_all(operation_element, "ownedParameter", "uml:Parameter", cls._parse_parameter)
        )

    @classmethod
    def _parse_parameter(cls, parameter_element: XmiElement) -> Parameter:
        return Parameter(
            parameter_element.get("id"),
            "parameter",
            parameter_element.get("type"),
            ParameterDirection(parameter_element.get("direction"))
        )
