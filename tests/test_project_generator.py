from pathlib import Path
from tempfile import TemporaryDirectory

from src.ProjectGenerator import ProjectGenerator
from tests.data.example_syntax import example_syntax


class TestProjectGenerator:
    expected_project_path = Path(__file__).parent / "data" / "output" / "Sample_Project"

    def test_generate_project(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(example_syntax, output_path)
            project_path = output_path / example_syntax.name
            assert self._are_dirs_identical(project_path, self.expected_project_path)

    def _are_dirs_identical(self, dir1: Path, dir2: Path) -> bool:
        if not (dir1.is_dir() and dir2.is_dir()):
            return False
        for path1, path2 in zip(dir1.glob("*"), dir2.glob("*")):
            if path1.name != path2.name:
                return False
            if path1.is_file():
                with open(path1, "r") as f1, open(path2, "r") as f2:
                    if not f1.read() == f2.read():
                        return False
            elif path1.is_dir():
                if not self._are_dirs_identical(path1, path2):
                    return False
        return True
