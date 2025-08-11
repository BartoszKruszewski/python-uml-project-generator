from pathlib import Path

from src.syntax import (
    Class,
    Package,
    Project
)
from src.TemplateManager import TemplateManager


class ProjectGenerator:
    def __init__(self, project: Project, root_dir: Path) -> None:
        self._template_manager = TemplateManager(project, root_dir)
        project_root = root_dir / project.name
        for package in project.packages:
            self._generate_package(project_root, package)

    def _generate_package(self, parent: Path, package: Package):
        package_path = parent / package.name
        package_path.mkdir(parents=True, exist_ok=True)
        for class_syntax in package.classes:
            self._generate_class(package_path, class_syntax)
        for subpackage in package.subpackages:
            self._generate_package(package_path, subpackage)

    def _generate_class(self, package_path: Path, class_syntax: Class):
        class_template = self._template_manager.generate_class(class_syntax)
        class_path = package_path / f"{class_syntax.name}.py"
        with open(class_path, "w") as f:
            f.write(class_template)
