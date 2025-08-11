from pathlib import Path
from tempfile import TemporaryDirectory

from src.ImportMapping import ImportMapping
from tests.data.example_syntax import example_syntax


class TestImportMapping:
    expected_mapping = {
        'ExampleService': 'output.Sample_Project.Core.ExampleService',
        'UserRepository': 'output.Sample_Project.Data.UserRepository',
        'TestSubclass': 'output.Sample_Project.Core.TestSubpackage.TestSubclass'
    }

    def test_import_mapping(self):
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            assert ImportMapping(example_syntax, output_dir)._mapping == self.expected_mapping
