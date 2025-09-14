from pathlib import Path

from project_generator.XmiParser import XmiParser
from tests.data.example_syntax import example_syntax


class TestXmiParser:
    test_xmi_path = Path(__file__).parent / "data" / "test.xmi"

    def test_parse(self):
        assert XmiParser.parse(self.test_xmi_path) == example_syntax
