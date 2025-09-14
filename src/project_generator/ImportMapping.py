from pathlib import Path

from project_generator.exceptions import NonMappedClass
from project_generator.syntax import (
    Package,
    Project
)


class ImportMapping:
    def __init__(self, project: Project, root_dir: Path) -> None:
        self._mapping: dict[str, str] = {}
        for package in project.packages:
            self._map_package(f"{root_dir.name}.{project.name}", package)

    def get_import_path(self, class_name: str) -> str:
        if class_name not in self._mapping:
            raise NonMappedClass()
        return self._mapping[class_name]

    def _map_package(self, parent_path: str, package: Package):
        actual_import_path = f"{parent_path}.{package.name}"
        for subpackage in package.subpackages:
            self._map_package(actual_import_path, subpackage)
        for class_syntax in package.classes:
            self._mapping[class_syntax.name] = f"{actual_import_path}.{class_syntax.name}"
