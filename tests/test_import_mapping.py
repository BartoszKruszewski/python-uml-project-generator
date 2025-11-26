from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from project_generator.ImportMapping import ImportMapping
from project_generator.exceptions import NonMappedClass
from project_generator.syntax import (
    Class,
    Package,
    Project,
)


class TestImportMappingExtended:
    def test_import_mapping_deeply_nested_packages(self):
        """Test import mapping for deeply nested packages."""
        project = Project(
            id="p1",
            name="TestProject",
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
                                    classes=[
                                        Class(
                                            id="c1",
                                            name="DeepClass",
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
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            path = import_mapping.get_import_path("DeepClass")
            assert path == "output.TestProject.Level1.Level2.Level3.DeepClass"

    def test_import_mapping_multiple_classes_same_package(self):
        project = Project(
            id="p1",
            name="TestProject",
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
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            path1 = import_mapping.get_import_path("Class1")
            path2 = import_mapping.get_import_path("Class2")
            path3 = import_mapping.get_import_path("Class3")

            assert path1 == "output.TestProject.Test.Class1"
            assert path2 == "output.TestProject.Test.Class2"
            assert path3 == "output.TestProject.Test.Class3"

    def test_import_mapping_classes_different_packages(self):
        project = Project(
            id="p1",
            name="TestProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Package1",
                    subpackages=[],
                    classes=[
                        Class(
                            id="c1",
                            name="ClassA",
                            properties=[],
                            operations=[],
                        )
                    ],
                    dependencies=[],
                    data_types=[],
                ),
                Package(
                    id="pkg2",
                    name="Package2",
                    subpackages=[],
                    classes=[
                        Class(
                            id="c2",
                            name="ClassB",
                            properties=[],
                            operations=[],
                        )
                    ],
                    dependencies=[],
                    data_types=[],
                ),
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            path_a = import_mapping.get_import_path("ClassA")
            path_b = import_mapping.get_import_path("ClassB")

            assert path_a == "output.TestProject.Package1.ClassA"
            assert path_b == "output.TestProject.Package2.ClassB"

    def test_import_mapping_non_existent_class(self):
        project = Project(
            id="p1",
            name="TestProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Test",
                    subpackages=[],
                    classes=[
                        Class(
                            id="c1",
                            name="ExistingClass",
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
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            with pytest.raises(NonMappedClass):
                import_mapping.get_import_path("NonExistentClass")

    def test_import_mapping_empty_project(self):
        project = Project(
            id="p1",
            name="EmptyProject",
            packages=[],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            with pytest.raises(NonMappedClass):
                import_mapping.get_import_path("AnyClass")

    def test_import_mapping_single_class_root_package(self):
        project = Project(
            id="p1",
            name="TestProject",
            packages=[
                Package(
                    id="pkg1",
                    name="Root",
                    subpackages=[],
                    classes=[
                        Class(
                            id="c1",
                            name="RootClass",
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
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            import_mapping = ImportMapping(project, output_dir)

            path = import_mapping.get_import_path("RootClass")
            assert path == "output.TestProject.Root.RootClass"

