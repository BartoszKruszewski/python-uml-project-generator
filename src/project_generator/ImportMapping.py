from pathlib import Path

from project_generator.exceptions import NonMappedClass
from project_generator.syntax import (
    Package,
    Project
)


class ImportMapping:
    """Module responsible for mapping class names to their import paths."""

    def __init__(self, project: Project, root_dir: Path) -> None:
        """
        Args:
            project: Project syntax object.
            root_dir: Path to the root directory of the project.
        """
        self._mapping: dict[str, str] = {}
        for package in project.packages:
            self._map_package(f"{root_dir.name}.{project.name}", package)

    def get_import_path(self, class_name: str) -> str:
        """Gets the import path for a given class name.

        Args:
            class_name: Name of the class to get the import path for.
        Returns:
            Import path of the class.
        """
        if class_name not in self._mapping:
            raise NonMappedClass()
        return self._mapping[class_name]

    def _map_package(self, parent_path: str, package: Package):
        """Recursively maps packages and their classes to import paths.

        Args:
            parent_path: Parent import path.
            package: Package syntax object.
        """
        actual_import_path = f"{parent_path}.{package.name}"
        for subpackage in package.subpackages:
            self._map_package(actual_import_path, subpackage)
        for class_syntax in package.classes:
            self._mapping[class_syntax.name] = f"{actual_import_path}.{class_syntax.name}"
