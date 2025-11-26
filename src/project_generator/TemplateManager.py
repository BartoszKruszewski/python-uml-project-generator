from pathlib import Path

from project_generator.Config import Config
from project_generator.ImportMapping import ImportMapping
from project_generator.syntax import (
    Class,
    Operation,
    ParameterDirection,
    Project,
    Relation,
    RelationType,
    Visibility
)


class TemplateManager:
    """Module responsible for managing templates for code generation."""

    class_body: str = """
{imports}class {class_name}{base_classes}:
{members}
"""

    constructor_body_header: str = "def __init__({args}):"

    method_body: str = """
def {method_name}({args}) -> {return_type}:
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

        # Process all relations - add imports for all types used in relations
        for relation in relations_for_class:
            if relation.type in (
                RelationType.ASSOCIATION,
                RelationType.AGGREGATION,
                RelationType.COMPOSITION,
            ):
                type_name = self._relation_type_for_imports(relation)
                if type_name not in Config.standard_data_types:
                    used_classes.add(type_name)
            elif relation.type in (
                RelationType.GENERALIZATION,
                RelationType.REALIZATION,
            ):
                if relation.supplier not in Config.standard_data_types:
                    used_classes.add(relation.supplier)
            # Note: DEPENDENCY relations don't require imports in constructor,
            # but if the type is used elsewhere, it will be caught by _get_used_classes

        import_lines = []
        for used_class in sorted(used_classes):
            try:
                import_path = self._import_mapping.get_import_path(used_class)
                import_lines.append(f"from {import_path} import {used_class}")
            except Exception:
                pass
        return "\n".join(import_lines)

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
            if typed_syntax.type
            and typed_syntax.type not in Config.standard_data_types
            and not typed_syntax.type.startswith("uml:")  # Filter out meta-types
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
        used_param_names: set[str] = set()

        for prop in class_syntax.properties:
            # Use property name directly (no underscore prefix in parameter)
            prop_name = prop.name
            # Default type to "Integer" if empty
            prop_type = prop.type if prop.type else "Integer"
            parameter_parts.append(
                f"{prop_name}: {self._get_type_string(prop_type)}"
            )
            # Generate assignment based on visibility
            if prop.visibility == Visibility.PRIVATE:
                # Private: self._priv = priv
                field_name = self._get_python_name(prop.name, prop.visibility)
                body_lines.append(f"self.{field_name} = {prop_name}")
            else:
                # Public: self.pub = pub
                body_lines.append(f"self.{prop_name} = {prop_name}")
            used_param_names.add(prop_name)

        # Process all relations, ensuring unique parameter names
        for relation in relations_for_class:
            supplier = relation.supplier or "Ref"
            base_param_name = supplier[0].lower() + supplier[1:] if supplier else "ref"
            type_name = self._get_type_string(supplier)

            # Generate unique parameter name
            param_name = base_param_name
            counter = 1
            while param_name in used_param_names:
                param_name = f"{base_param_name}{counter}"
                counter += 1
            used_param_names.add(param_name)

            if relation.type == RelationType.ASSOCIATION:
                param = f"{param_name}: {type_name} | None = None"
                parameter_parts.append(param)
                body_lines.append(f"self._{param_name} = {param_name}")

            elif relation.type == RelationType.AGGREGATION:
                list_name = param_name + "s"
                # Ensure list name is also unique
                original_list_name = list_name
                counter = 1
                while list_name in used_param_names:
                    list_name = f"{original_list_name}{counter}"
                    counter += 1
                used_param_names.add(list_name)

                param = f"{list_name}: list[{type_name}] | None = None"
                parameter_parts.append(param)
                body_lines.append(
                    f"self._{list_name} = {list_name} or []"
                )

            elif relation.type == RelationType.COMPOSITION:
                field_name = param_name
                # Ensure field name is unique for composition
                original_field_name = field_name
                counter = 1
                while field_name in used_param_names:
                    field_name = f"{original_field_name}{counter}"
                    counter += 1
                used_param_names.add(field_name)

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
                method_name=self._get_python_name(operation.name, operation.visibility),
                args=self._format_method_args(
                    parameter
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

    def _format_method_args(self, parameters) -> str:
        """Formats method arguments string.

        Args:
            parameters: Iterable of Parameter objects.
        Returns:
            Formatted arguments string (e.g., "self, arg1: int" or just "self").
        """
        param_list = list(parameters)
        if not param_list:
            return "self"
        param_strs = [
            f"{parameter.name}: {self._get_type_string(parameter.type)}"
            for parameter in param_list
        ]
        return "self, " + ", ".join(param_strs)

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
    def _get_python_name(name: str, visibility: Visibility) -> str:
        """Gets the Python name with underscore prefix for private members.

        Args:
            name: Original name.
            visibility: Visibility of the property or operation.
        Returns:
            Name with underscore prefix if private, otherwise original name.
        """
        if visibility == Visibility.PRIVATE:
            # Add underscore prefix if not already present
            return name if name.startswith("_") else f"_{name}"
        return name

    @staticmethod
    def _get_type_string(data_type_name: str) -> str:
        """Gets the string representation of a data type.

        Args:
            data_type_name: Name of the data type.
        Returns:
            String representation of the data type.
        """
        return Config.standard_data_types.get(data_type_name, data_type_name)
