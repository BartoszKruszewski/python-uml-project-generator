from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from project_generator.XmiParser import XmiParser
from project_generator.exceptions import XmiParserException
from project_generator.syntax import RelationType


class TestXmiParserExtended:
    def test_parse_empty_package(self):
        """Test parsing XMI with empty package."""
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="EmptyProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="EmptyPackage"/>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "empty.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            assert project.name == "EmptyProject"
            assert len(project.packages) == 1
            assert project.packages[0].name == "EmptyPackage"
            assert len(project.packages[0].classes) == 0
            assert len(project.packages[0].subpackages) == 0

    def test_parse_class_without_properties_or_operations(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="TestProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="Test">
      <packagedElement xmi:type="uml:Class" xmi:id="class1" name="EmptyClass"/>
    </packagedElement>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "empty_class.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            assert len(project.packages[0].classes) == 1
            assert project.packages[0].classes[0].name == "EmptyClass"
            assert len(project.packages[0].classes[0].properties) == 0
            assert len(project.packages[0].classes[0].operations) == 0

    def test_parse_nested_packages(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="TestProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="Outer">
      <packagedElement xmi:type="uml:Package" xmi:id="pkg2" name="Inner">
        <packagedElement xmi:type="uml:Class" xmi:id="class1" name="InnerClass"/>
      </packagedElement>
    </packagedElement>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "nested.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            assert len(project.packages) == 1
            outer = project.packages[0]
            assert outer.name == "Outer"
            assert len(outer.subpackages) == 1
            inner = outer.subpackages[0]
            assert inner.name == "Inner"
            assert len(inner.classes) == 1
            assert inner.classes[0].name == "InnerClass"

    def test_parse_all_relation_types(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="TestProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="Test">
      <packagedElement xmi:type="uml:Class" xmi:id="c1" name="Class1"/>
      <packagedElement xmi:type="uml:Class" xmi:id="c2" name="Class2"/>
      <packagedElement xmi:type="uml:Association" xmi:id="r1" name="assoc" client="Class1" supplier="Class2"/>
      <packagedElement xmi:type="uml:Aggregation" xmi:id="r2" name="agg" client="Class1" supplier="Class2"/>
      <packagedElement xmi:type="uml:Composition" xmi:id="r3" name="comp" client="Class1" supplier="Class2"/>
      <packagedElement xmi:type="uml:Dependency" xmi:id="r4" name="dep" client="Class1" supplier="Class2"/>
      <packagedElement xmi:type="uml:Generalization" xmi:id="r5" name="gen" client="Class1" supplier="Class2"/>
      <packagedElement xmi:type="uml:Realization" xmi:id="r6" name="real" client="Class1" supplier="Class2"/>
    </packagedElement>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "relations.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            relations = project.packages[0].dependencies
            assert len(relations) == 6

            relation_types = [r.type for r in relations]
            assert RelationType.ASSOCIATION in relation_types
            assert RelationType.AGGREGATION in relation_types
            assert RelationType.COMPOSITION in relation_types
            assert RelationType.DEPENDENCY in relation_types
            assert RelationType.GENERALIZATION in relation_types
            assert RelationType.REALIZATION in relation_types

    def test_parse_invalid_xml(self):
        invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="Test">
    <unclosed_tag>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "invalid.xml"
            xmi_path.write_text(invalid_xml)

            with pytest.raises(Exception):  # XML parsing error
                XmiParser.parse(xmi_path)

    def test_parse_missing_model_element(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "no_model.xmi"
            xmi_path.write_text(xmi_content)

            with pytest.raises(XmiParserException):
                XmiParser.parse(xmi_path)

    def test_parse_property_without_type(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="TestProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="Test">
      <packagedElement xmi:type="uml:Class" xmi:id="class1" name="TestClass">
        <ownedAttribute xmi:type="uml:Property" xmi:id="prop1" name="value" visibility="private"/>
      </packagedElement>
    </packagedElement>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "no_type.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            prop = project.packages[0].classes[0].properties[0]
            assert prop.name == "value"
            # Type should be empty string or default
            assert prop.type == "" or prop.type is not None

    def test_parse_operation_without_parameters(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="TestProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="Test">
      <packagedElement xmi:type="uml:Class" xmi:id="class1" name="TestClass">
        <ownedOperation xmi:type="uml:Operation" xmi:id="op1" name="doSomething" visibility="public"/>
      </packagedElement>
    </packagedElement>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "no_params.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            op = project.packages[0].classes[0].operations[0]
            assert op.name == "doSomething"
            assert len(op.parameters) == 0

    def test_parse_multiple_classes_in_package(self):
        xmi_content = """<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">
  <uml:Model xmi:type="uml:Model" xmi:id="model_1" name="TestProject">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg1" name="Test">
      <packagedElement xmi:type="uml:Class" xmi:id="c1" name="Class1"/>
      <packagedElement xmi:type="uml:Class" xmi:id="c2" name="Class2"/>
      <packagedElement xmi:type="uml:Class" xmi:id="c3" name="Class3"/>
    </packagedElement>
  </uml:Model>
</xmi:XMI>"""

        with TemporaryDirectory() as temp_dir:
            xmi_path = Path(temp_dir) / "multiple.xmi"
            xmi_path.write_text(xmi_content)

            project = XmiParser.parse(xmi_path)

            assert len(project.packages[0].classes) == 3
            class_names = [c.name for c in project.packages[0].classes]
            assert "Class1" in class_names
            assert "Class2" in class_names
            assert "Class3" in class_names
