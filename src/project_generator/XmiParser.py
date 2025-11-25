from functools import partial
from pathlib import Path
from typing import (
    Callable,
    TypeVar
)
from xml.etree import ElementTree as ET

from project_generator.syntax import (
    AbstractSyntax,
    Class,
    DataType,
    Operation,
    Package,
    Parameter,
    ParameterDirection,
    Project,
    Property,
    Relation,
    RelationType,
    Visibility
)
from project_generator.XmiElement import XmiElement


class XmiParser:
    """XMI parser module to convert XMI files into project syntax objects."""

    T = TypeVar("T", bound="AbstractSyntax")

    @classmethod
    def parse(cls, xmi_path: Path) -> Project:
        """Main parsing method to parse an XMI file into a Project syntax object.

        Args:
            xmi_path: Path to the XMI file.
        Returns:
            Parsed Project syntax object.
        """
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
        """Helpers method to parse all child elements of a given type.

        Args:
            parent: Parent XmiElement to search within.
            element_name: Name of the child elements to find.
            uml_type: UML type to filter by.
            parser: Parser function to convert XmiElement to the desired syntax object.
        Returns:
            List of parsed syntax objects.
        """
        return [
            parser(element)
            for element in parent.find(element_name, True)
            if element.get("type", True) == uml_type
        ]

    @classmethod
    def _parse_package(cls, package_element: XmiElement) -> Package:
        """Parses a package element into a Package syntax object.

        Args:
            package_element: XMI element representing the package.
        Returns:
            Parsed Package syntax object.
        """
        return Package(
            *package_element.syganture,
            cls._parse_all(package_element, "packagedElement", "uml:Package", cls._parse_package),
            cls._parse_all(package_element, "packagedElement", "uml:Class", cls._parse_class),
            sum([
                cls._parse_all(
                    package_element,
                    "packagedElement",
                    f"uml:{relation.capitalize()}",
                    partial(cls._parse_relation, relation)
                )
                for relation in [
                    "association",
                    "dependency",
                    "aggregation",
                    "composition",
                    "realization",
                    "generalization"
                ]
            ], []),
            cls._parse_all(package_element, "packagedElement", "uml:DataType", cls._parse_data_type),
        )

    @classmethod
    def _parse_relation(cls, name: str, relation_element: XmiElement) -> Relation:
        """Parses a relation element into a relation syntax object.

        Args:
            relation_element: XMI element representing the relation.
        Returns:
            Relation syntax object.
        """
        return Relation(
            *relation_element.syganture,
            RelationType(name),
            relation_element.get("client"),
            relation_element.get("supplier")
        )

    @classmethod
    def _parse_data_type(cls, data_type_element: XmiElement) -> DataType:
        """Parses a data type element into a DataType syntax object.

        Args:
            data_type_element: XMI element representing the data type.
        Returns:
            Data type syntax object.
        """
        return DataType(*data_type_element.syganture)

    @classmethod
    def _parse_class(cls, class_element: XmiElement) -> Class:
        """Parses a class element into a class syntax object.

        Args:
            data_type_element: XMI element representing the class.
        Returns:
            Class syntax object.
        """
        return Class(
            *class_element.syganture,
            cls._parse_all(class_element, "ownedAttribute", "uml:Property", cls._parse_property),
            cls._parse_all(class_element, "ownedOperation", "uml:Operation", cls._parse_operation)
        )

    @classmethod
    def _parse_property(cls, property_element: XmiElement) -> Property:
        """Parses a property element into a property syntax object.

        Args:
            property_element: XMI element representing the property.
        Returns:
            Property syntax object.
        """
        # Get type attribute directly from XML element (without namespace)
        # to avoid confusion with xmi:type meta-attribute which has value "uml:Property"
        prop_type = ""
        element = property_element._element
        # Check for 'type' attribute without namespace (direct attribute access)
        if (type_attr := element.get("type")) is not None:
            prop_type = type_attr.strip()
            # Filter out meta-types - if type equals "uml:Property", it's a meta-type, not actual type
            if prop_type == "uml:Property" or prop_type.startswith("uml:"):
                prop_type = ""

        return Property(
            *property_element.syganture,
            prop_type,
            Visibility(property_element.get("visibility"))
        )

    @classmethod
    def _parse_operation(cls, operation_element: XmiElement) -> Operation:
        """Parses an operation element into an operation syntax object.

        Args:
            operation_element: XMI element representing the operation.
        Returns:
            Operation syntax object.
        """
        return Operation(
            *operation_element.syganture,
            cls._parse_all(operation_element, "ownedParameter", "uml:Parameter", cls._parse_parameter),
            Visibility(operation_element.get("visibility"))
        )

    @classmethod
    def _parse_parameter(cls, parameter_element: XmiElement) -> Parameter:
        """Parses a parameter element into an parameter syntax object.

        Args:
            parameter_element: XMI element representing the parameter.
        Returns:
            Parameter syntax object.
        """
        direction = ParameterDirection(parameter_element.get("direction"))
        return Parameter(
            parameter_element.get("id"),
            "" if direction == ParameterDirection.RETURN else parameter_element.get("name"),
            parameter_element.get("type"),
            direction
        )
