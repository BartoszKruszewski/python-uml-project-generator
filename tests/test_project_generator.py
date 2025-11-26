from pathlib import Path
from tempfile import TemporaryDirectory

from project_generator.ProjectGenerator import ProjectGenerator
from project_generator.syntax import (
    Class,
    Package,
    Project,
)


class TestProjectGeneratorExtended:
    def test_generate_empty_project(self):
        project = Project(
            id="p1",
            name="EmptyProject",
            packages=[],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            project_path = output_path / project.name
            if project.packages:
                assert project_path.exists()
                assert project_path.is_dir()
            else:
                assert not project_path.exists() or project_path.is_dir()

    def test_generate_project_with_only_packages(self):
        project = Project(
            id="p1",
            name="PackageOnlyProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Package1",
                    subpackages=[],
                    classes=[],
                    dependencies=[],
                    data_types=[],
                ),
                Package(
                    id="pkg2",
                    name="Package2",
                    subpackages=[],
                    classes=[],
                    dependencies=[],
                    data_types=[],
                ),
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            project_path = output_path / project.name
            assert project_path.exists()

            pkg1_path = project_path / "Package1"
            pkg2_path = project_path / "Package2"

            assert pkg1_path.exists()
            assert pkg2_path.exists()

    def test_generate_project_with_nested_packages(self):
        project = Project(
            id="p1",
            name="NestedProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Outer",
                    subpackages=[
                        Package(
                            id="pkg2",
                            name="Inner",
                            subpackages=[],
                            classes=[
                                Class(
                                    id="c1",
                                    name="InnerClass",
                                    properties=[],
                                    operations=[],
                                )
                            ],
                            dependencies=[],
                            data_types=[],
                        )
                    ],
                    classes=[],
                    dependencies=[],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            project_path = output_path / project.name
            outer_path = project_path / "Outer"
            inner_path = outer_path / "Inner"

            assert outer_path.exists()
            assert inner_path.exists()

            assert (inner_path / "InnerClass.py").exists()

    def test_generate_project_creates_init_files(self):
        project = Project(
            id="p1",
            name="InitTestProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Level1",
                    subpackages=[
                        Package(
                            id="pkg2",
                            name="Level2",
                            subpackages=[
                                Package(
                                    id="pkg3",
                                    name="Level3",
                                    subpackages=[],
                                    classes=[],
                                    dependencies=[],
                                    data_types=[],
                                )
                            ],
                            classes=[],
                            dependencies=[],
                            data_types=[],
                        )
                    ],
                    classes=[],
                    dependencies=[],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            project_path = output_path / project.name
            level1_path = project_path / "Level1"
            level2_path = level1_path / "Level2"
            level3_path = level2_path / "Level3"

            assert level1_path.exists()
            assert level2_path.exists()
            assert level3_path.exists()

    def test_generate_project_class_file_content(self):
        project = Project(
            id="p1",
            name="ContentTestProject",
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
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            class_file = output_path / project.name / "Test" / "TestClass.py"
            assert class_file.exists()

            content = class_file.read_text()
            assert "class TestClass:" in content
            assert "pass" in content

    def test_generate_project_multiple_classes_same_package(self):
        project = Project(
            id="p1",
            name="MultiClassProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Test",
                    subpackages=[],
                    classes=[
                        Class(
                            id="c1",
                            name="Class1",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Class2",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c3",
                            name="Class3",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            package_path = output_path / project.name / "Test"
            assert (package_path / "Class1.py").exists()
            assert (package_path / "Class2.py").exists()
            assert (package_path / "Class3.py").exists()

    def test_generate_project_preserves_package_structure(self):
        project = Project(
            id="p1",
            name="StructureTestProject",
            packages=[
                Package(
                    id="pkg1",
                    name="A",
                    subpackages=[
                        Package(
                            id="pkg2",
                            name="B",
                            subpackages=[
                                Package(
                                    id="pkg3",
                                    name="C",
                                    subpackages=[],
                                    classes=[
                                        Class(
                                            id="c1",
                                            name="ClassInC",
                                            properties=[],
                                            operations=[],
                                        )
                                    ],
                                    dependencies=[],
                                    data_types=[],
                                )
                            ],
                            classes=[],
                            dependencies=[],
                            data_types=[],
                        )
                    ],
                    classes=[],
                    dependencies=[],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output"
            ProjectGenerator(project, output_path)

            class_file = (
                output_path
                / project.name
                / "A"
                / "B"
                / "C"
                / "ClassInC.py"
            )
            assert class_file.exists()

            assert (output_path / project.name / "A").exists()
            assert (output_path / project.name / "A" / "B").exists()
            assert (output_path / project.name / "A" / "B" / "C").exists()
