from pathlib import Path

from project_generator.Config import Config
from project_generator.ImportMapping import ImportMapping
from project_generator.syntax import (
    Class,
    Operation,
    ParameterDirection,
    Project,
    Property
)


class TemplateManager:
    class_body: str = """
{imports}class {class_name}:
{methods}
"""

    constructor_body: str = """
def __init__(self, {args}):
    {assignments}
"""
    method_body: str = """
def {method_name}(self, {args}) -> {return_type}:
    pass
"""

    def __init__(self, project: Project, root_dir: Path) -> None:
        self._import_mapping = ImportMapping(project, root_dir)

    def generate_class(self, class_syntax: Class) -> str:
        return self.class_body.strip().format(
            imports=(imports + "\n\n\n") if (imports := self._generate_imports(class_syntax)) else "",
            class_name=class_syntax.name,
            methods=self._indent_block(
                (self._generate_constructor(class_syntax.properties) if class_syntax.properties else "")
                + ("\n\n" if class_syntax.properties and class_syntax.operations else "")
                + (self._generate_methods(class_syntax.operations) if class_syntax.operations else ""),
                indent=4
            )
        ) + "\n"

    def _generate_imports(self, class_syntax: Class) -> str:
        return "\n".join(
            f"from {self._import_mapping.get_import_path(used_class)} import {used_class}"
            for used_class in self._get_used_classes(class_syntax)
        )

    def _get_used_classes(self, class_syntax: Class) -> list[str]:
        return [
            typed_syntax.type for typed_syntax in
            (
                class_syntax.properties +
                [
                    parameter for operation in class_syntax.operations
                    for parameter in operation.parameters
                ]
            )
            if typed_syntax.type not in Config.standard_data_types
        ]

    def _generate_constructor(self, properties: list[Property]) -> str:
        return self.constructor_body.strip().format(
            args=", ".join(f"{property.name}: {self._get_type_string(property.type)}" for property in properties),
            assignments="\n    ".join(f"self._{property.name} = {property.name}" for property in properties)
        )

    def _generate_methods(self, operations: list[Operation]) -> str:
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
                    if (return_types := [
                        parameter.type for parameter in operation.parameters
                        if parameter.direction == ParameterDirection.RETURN
                    ])
                    else "None"
                )
            )
            for operation in operations
        )

    @staticmethod
    def _indent_block(block: str, indent: int) -> str:
        return "\n".join((" " * indent + line) if line != "" else line for line in block.split("\n"))

    @staticmethod
    def _get_type_string(data_type_name: str) -> str:
        return Config.standard_data_types.get(data_type_name, data_type_name)
