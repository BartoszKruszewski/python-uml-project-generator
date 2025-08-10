from src.syntax import (
    Class,
    Operation,
    Parameter,
    ParameterDirection,
    Property
)
from src.TemplateManager import TemplateManager


class TestTemplateManager:
    test_class = Class(
        "example_class_id",
        "example_class_name",
        [
            Property(
                "example_property_id1",
                "example_property_name1",
                "String"
            ),
            Property(
                "example_property_id2",
                "example_property_name2",
                "String"
            )
        ],
        [
            Operation(
                "example_operation_id1",
                "exmaple_operation_name1",
                [
                    Parameter(
                        "example_parameter_id1",
                        "example_parameter_name1",
                        "String",
                        ParameterDirection.IN
                    ),
                    Parameter(
                        "example_parameter_id2",
                        "example_parameter_name2",
                        "String",
                        ParameterDirection.IN
                    ),
                    Parameter(
                        "example_return_parameter_id1",
                        "example_return_parameter_name1",
                        "String",
                        ParameterDirection.RETURN
                    )
                ]
            ),
            Operation(
                "example_operation_id2",
                "exmaple_operation_name2",
                [
                    Parameter(
                        "example_parameter_id3",
                        "example_parameter_name3",
                        "String",
                        ParameterDirection.IN
                    ),
                    Parameter(
                        "example_parameter_id4",
                        "example_parameter_name4",
                        "String",
                        ParameterDirection.IN
                    ),
                    Parameter(
                        "example_return_parameter_id2",
                        "example_return_parameter_name2",
                        "String",
                        ParameterDirection.RETURN
                    )
                ]
            )
        ]
    )
    expected = """
imports


class example_class_name:
    def __init__(self, example_property_name1: String, example_property_name2: String):
        self._example_property_name1 = example_property_name1
        self._example_property_name2 = example_property_name2

    def exmaple_operation_name1(self, example_parameter_name1: String, example_parameter_name2: String) -> String:
        pass

    def exmaple_operation_name2(self, example_parameter_name3: String, example_parameter_name4: String) -> String:
        pass
"""

    def test_generate_class(self):
        assert TemplateManager.generate_class(self.test_class) == self.expected.strip() + "\n"
