from pathlib import Path

from src.syntax import (
    Class,
    Package,
    Project
)
from src.TemplateManager import TemplateManager


class ProjectGenerator:
    @classmethod
    def generate_project(cls, project: Project, output_dir: Path):
        project_root = output_dir / project.name
        for package in project.packages:
            cls._generate_package(project_root, package)

    @classmethod
    def _generate_package(cls, parent: Path, package: Package):
        package_path = parent / package.name
        package_path.mkdir(parents=True, exist_ok=True)
        for class_syntax in package.classes:
            cls._generate_class(package_path, class_syntax)

    @classmethod
    def _generate_class(cls, package_path: Path, class_syntax: Class):
        class_template = TemplateManager.generate_class(class_syntax)
        class_path = package_path / f"{class_syntax.name}.py"
        with open(class_path, "w") as f:
            f.write(class_template)
