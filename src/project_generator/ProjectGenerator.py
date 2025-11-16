from pathlib import Path

from project_generator.syntax import (
    Class,
    Package,
    Project,
    Relation
)
from project_generator.TemplateManager import TemplateManager


class ProjectGenerator:
    """Module responsible for generating the project structure and files."""

    def __init__(self, project: Project, root_dir: Path) -> None:
        """
        Args:
            project: Project syntax object.
            root_dir: Root directory where the project will be generated.
        """
        self._template_manager = TemplateManager(project, root_dir)
        self._relations_by_client: dict[str, list[Relation]] = {}
        self._index_relations(project)

        project_root = root_dir / project.name
        for package in project.packages:
            self._generate_package(project_root, package)

    def _index_relations(self, project: Project) -> None:
        """Builds map: class name -> list of relations where it is the client.

        Args:
            project: Project syntax object.
        """

        def visit_package(pkg: Package) -> None:
            for relation in pkg.dependencies:
                self._relations_by_client.setdefault(
                    relation.client, []
                ).append(relation)
            for sub in pkg.subpackages:
                visit_package(sub)

        for pkg in project.packages:
            visit_package(pkg)

    def _generate_package(self, parent: Path, package: Package) -> None:
        """Generates a package directory and its contents.

        Args:
            parent: Path to the parent directory.
            package: Package syntax object.
        """
        package_path = parent / package.name
        package_path.mkdir(parents=True, exist_ok=True)
        for class_syntax in package.classes:
            self._generate_class(package_path, class_syntax)
        for subpackage in package.subpackages:
            self._generate_package(package_path, subpackage)

    def _generate_class(self, package_path: Path, class_syntax: Class) -> None:
        """Generates a class file from its syntax object.

        Args:
            package_path: Path to the package directory.
            class_syntax: Class syntax object.
        """
        relations_for_class = self._relations_by_client.get(
            class_syntax.name, []
        )
        class_template = self._template_manager.generate_class(
            class_syntax,
            relations_for_class,
        )
        class_path = package_path / f"{class_syntax.name}.py"
        with open(class_path, "w") as f:
            f.write(class_template)
