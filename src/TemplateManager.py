from src.syntax import (
    Class,
    Operation,
    ParameterDirection,
    Property
)


class TemplateManager:
    class_body: str = """
{imports}


class {class_name}:
{constructor}

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

    @classmethod
    def generate_class(cls, class_syntax: Class) -> str:
        return cls.class_body.strip().format(
            imports="imports",
            class_name=class_syntax.name,
            constructor=cls._indent_block(cls._generate_constructor(class_syntax.properties), indent=4),
            methods=cls._indent_block(cls._generate_methods(class_syntax.operations), indent=4)
        ) + "\n"

    @classmethod
    def _generate_constructor(cls, properties: list[Property]) -> str:
        return cls.constructor_body.strip().format(
            args=", ".join(f"{property.name}: {property.type}" for property in properties),
            assignments="\n    ".join(f"self._{property.name} = {property.name}" for property in properties)
        )

    @classmethod
    def _generate_methods(cls, operations: list[Operation]) -> str:
        return "\n\n".join(
            cls.method_body.strip().format(
                method_name=operation.name,
                args=", ".join(
                    f"{parameter.name}: {parameter.type}"
                    for parameter in operation.parameters
                    if parameter.direction == ParameterDirection.IN
                ),
                return_type=next(
                    parameter.type for parameter in operation.parameters
                    if parameter.direction == ParameterDirection.RETURN
                )
            )
            for operation in operations
        )

    @staticmethod
    def _indent_block(block: str, indent: int) -> str:
        return "\n".join((" " * indent + line) if line != "" else line for line in block.split("\n"))
