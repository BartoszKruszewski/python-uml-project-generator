from pathlib import Path

from project_generator.Config import Config
from project_generator.ImportMapping import ImportMapping
from project_generator.syntax import (
    Class,
    Operation,
    ParameterDirection,
    Project,
    Relation,
    RelationType
)


class TemplateManager:
    """Module responsible for managing templates for code generation."""

    class_body: str = """
{imports}class {class_name}{base_classes}:
{members}
"""

    constructor_body_header: str = "def __init__({args}):"

    method_body: str = """
def {method_name}(self, {args}) -> {return_type}:
    pass
"""

    def __init__(self, project: Project, root_dir: Path) -> None:
        """
        Args:
            project: Project syntax object.
            root_dir: Root directory where the project will be generated.
        """
        self._import_mapping = ImportMapping(project, root_dir)

    def generate_class(self, class_syntax: Class, relations_for_class: list[Relation]) -> str:
        """Generates the class code from its syntax object.

        Args:
            class_syntax: Class syntax object.
            relations_for_class: Relations where this class is the client.
        Returns:
            String containing the generated class code.
        """
        base_classes = self._get_base_classes(relations_for_class)
        base_classes_str = f"({', '.join(base_classes)})" if base_classes else ""

        imports = self._generate_imports(class_syntax, relations_for_class)

        members_parts: list[str] = []

        ctor_code = self._generate_constructor(
            class_syntax, relations_for_class)
        if ctor_code:
            members_parts.append(ctor_code)

        methods_code = self._generate_methods(class_syntax.operations)
        if methods_code:
            members_parts.append(methods_code)

        members_block = "\n\n".join(members_parts) if members_parts else "pass"

        return self.class_body.strip().format(
            imports=(imports + "\n\n\n") if imports else "",
            class_name=class_syntax.name,
            base_classes=base_classes_str,
            members=self._indent_block(members_block, indent=4),
        ) + "\n"

    def _get_base_classes(self, relations_for_class: list[Relation]) -> list[str]:
        """Returns list of base class names for generalization/realization.

        Args:
            relations_for_class: Relations where this class is the client.
        Returns:
            List of base class names.
        """
        bases: list[str] = []
        for relation in relations_for_class:
            if relation.type in (
                RelationType.GENERALIZATION,
                RelationType.REALIZATION,
            ):
                if relation.supplier not in bases:
                    bases.append(relation.supplier)
        return bases

    def _generate_imports(self, class_syntax: Class, relations_for_class: list[Relation]) -> str:
        """Generates import statements for the class based on its used types.

        Args:
            class_syntax: Class syntax object.
            relations_for_class: Relations where this class is the client.
        Returns:
            String containing import statements.
        """
        used_classes: set[str] = set(self._get_used_classes(class_syntax))

        for relation in relations_for_class:
            if relation.type in (
                RelationType.ASSOCIATION,
                RelationType.AGGREGATION,
                RelationType.COMPOSITION,
            ):
                type_name = self._relation_type_for_imports(relation)
                if type_name not in Config.standard_data_types:
                    used_classes.add(type_name)

        for relation in relations_for_class:
            if relation.type in (
                RelationType.GENERALIZATION,
                RelationType.REALIZATION,
            ):
                if relation.supplier not in Config.standard_data_types:
                    used_classes.add(relation.supplier)

        return "\n".join(
            f"from {self._import_mapping.get_import_path(used_class)} import {used_class}"
            for used_class in sorted(used_classes)
        )

    def _relation_type_for_imports(self, relation: Relation) -> str:
        """Type name used for import resolution (always supplier).

        Args:
            relation: Relation syntax object.
        Returns:
            Type name used for import resolution.
        """
        return relation.supplier

    def _get_used_classes(self, class_syntax: Class) -> list[str]:
        """Gets a list of class names used by the given class syntax.

        Args:
            class_syntax: Class syntax object.
        Returns:
            List of used class names.
        """
        return [
            typed_syntax.type
            for typed_syntax in (
                class_syntax.properties
                + [
                    parameter
                    for operation in class_syntax.operations
                    for parameter in operation.parameters
                ]
            )
            if typed_syntax.type not in Config.standard_data_types
        ]

    def _generate_constructor(self, class_syntax: Class, relations_for_class: list[Relation]) -> str:
        """Generates constructor with parameters based on properties and relations.

        - normal properties,
        - association / aggregation parameters,
        - composition created inside.

        Args:
            class_syntax: Class syntax object.
            relations_for_class: Relations where this class is the client.
        Returns:
            String containing the constructor code.
        """
        parameter_parts: list[str] = []
        body_lines: list[str] = []

        for prop in class_syntax.properties:
            parameter_parts.append(
                f"{prop.name}: {self._get_type_string(prop.type)}"
            )
            body_lines.append(f"self._{prop.name} = {prop.name}")

        for relation in relations_for_class:
            supplier = relation.supplier or "Ref"
            param_name = supplier[0].lower(
            ) + supplier[1:] if supplier else "ref"
            type_name = self._get_type_string(supplier)

            if relation.type == RelationType.ASSOCIATION:
                param = f"{param_name}: {type_name} | None = None"
                parameter_parts.append(param)
                body_lines.append(f"self._{param_name} = {param_name}")

            elif relation.type == RelationType.AGGREGATION:
                list_name = param_name + "s"
                param = f"{list_name}: list[{type_name}] | None = None"
                parameter_parts.append(param)
                body_lines.append(
                    f"self._{list_name} = {list_name} or []"
                )

            elif relation.type == RelationType.COMPOSITION:
                field_name = param_name
                body_lines.append(
                    f"self._{field_name} = {type_name}()"
                )

        if not parameter_parts and not body_lines:
            return ""

        if parameter_parts:
            args = "self, " + ", ".join(parameter_parts)
        else:
            args = "self"

        header = self.constructor_body_header.format(args=args)
        if not body_lines:
            body_lines = ["pass"]

        lines = [header] + [f"    {line}" for line in body_lines]
        return "\n".join(lines)

    def _generate_methods(self, operations: list[Operation]) -> str:
        """Generates method definitions for the class.

        Args:
            operations: List of operation syntax objects.
        Returns:
            String containing method definitions.
        """
        if not operations:
            return ""
        return "\n\n".join(
            self.method_body.strip().format(
                method_name=operation.name,
                args=", ".join(
                    f"{parameter.name}: {self._get_type_string(parameter.type)}"
                    for parameter in operation.parameters
                    if parameter.direction == ParameterDirection.IN
                ),
                return_type=self._get_type_string(
                    return_types[0]
                    if (
                        return_types := [
                            parameter.type
                            for parameter in operation.parameters
                            if parameter.direction == ParameterDirection.RETURN
                        ]
                    )
                    else "None"
                ),
            )
            for operation in operations
        )

    @staticmethod
    def _indent_block(block: str, indent: int) -> str:
        """Indents each line of the given block by the specified number of spaces.

        Args:
            block: String block to indent.
            indent: Number of spaces to indent.
        Returns:
            String containing the indented block.
        """
        if not block:
            return ""
        return "\n".join(
            (" " * indent + line) if line != "" else line
            for line in block.split("\n")
        )

    @staticmethod
    def _get_type_string(data_type_name: str) -> str:
        """Gets the string representation of a data type.

        Args:
            data_type_name: Name of the data type.
        Returns:
            String representation of the data type.
        """
        return Config.standard_data_types.get(data_type_name, data_type_name)
