from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from project_generator.exceptions import (
    NonMappedClass,
    XmiParserException,
)
from project_generator.ImportMapping import ImportMapping
from project_generator.XmiParser import XmiParser
from project_generator.syntax import (
    Class,
    Package,
    Project,
)


class TestExceptions:
    def test_no_attribute_exception(self):
        invalid_xmi = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1">
    <packagedElement xmi:type="uml:Class" xmi:id="class1"/>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "invalid.xmi"
            xmi_path.write_text(invalid_xmi)

            with pytest.raises(XmiParserException):
                XmiParser.parse(xmi_path)

    def test_no_element_exception(self):
        """Test NoElement exception is raised for missing elements."""

        invalid_xmi = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "invalid.xmi"
            xmi_path.write_text(invalid_xmi)

            with pytest.raises(XmiParserException):
                XmiParser.parse(xmi_path)

    def test_non_mapped_class_exception(self):
        project = Project(
            id="p1",
            name="TestProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Test",
                    subpackages=[],
                    classes=[
                        Class(
                            id="c1",
                            name="TestClass",
                            properties=[],
                            operations=[],
                        )
                    ],
                    dependencies=[],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            with pytest.raises(NonMappedClass):
                import_mapping.get_import_path("NonExistentClass")
