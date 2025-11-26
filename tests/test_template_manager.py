from pathlib import Path
from tempfile import TemporaryDirectory

from project_generator.ImportMapping import ImportMapping
from project_generator.TemplateManager import TemplateManager
from project_generator.syntax import (
    Class,
    Operation,
    Parameter,
    ParameterDirection,
    Project,
    Property,
    Relation,
    RelationType,
    Visibility,
    Package,
)


class TestTemplateManager:
    def test_generate_class_with_properties(self):
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
                            name="TestClass",
                            properties=[
                                Property(
                                    id="p1",
                                    name="id",
                                    type="String",
                                    visibility=Visibility.PRIVATE,
                                ),
                                Property(
                                    id="p2",
                                    name="name",
                                    type="String",
                                    visibility=Visibility.PUBLIC,
                                ),
                            ],
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
            manager = TemplateManager(project, output_dir)

            class_syntax = project.packages[0].classes[0]
            code = manager.generate_class(class_syntax, [])

            assert "class TestClass:" in code
            assert "def __init__(self, id: str, name: str):" in code
            assert "self._id = id" in code
            assert "self.name = name" in code

    def test_generate_class_with_association(self):
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
                            name="Client",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Service",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="uses",
                            type=RelationType.ASSOCIATION,
                            client="Client",
                            supplier="Service",
                        )
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            client_class = project.packages[0].classes[0]
            relations = [project.packages[0].dependencies[0]]
            code = manager.generate_class(client_class, relations)

            assert "from" in code  # Should have imports
            assert "service: Service | None = None" in code
            assert "self._service = service" in code

    def test_generate_class_with_multiple_associations(self):
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
                            name="Client",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Service",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c3",
                            name="Repository",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="uses1",
                            type=RelationType.ASSOCIATION,
                            client="Client",
                            supplier="Service",
                        ),
                        Relation(
                            id="r2",
                            name="uses2",
                            type=RelationType.ASSOCIATION,
                            client="Client",
                            supplier="Repository",
                        ),
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            client_class = project.packages[0].classes[0]
            relations = project.packages[0].dependencies
            code = manager.generate_class(client_class, relations)

            assert "service: Service | None = None" in code
            assert "repository: Repository | None = None" in code
            assert "self._service = service" in code
            assert "self._repository = repository" in code

    def test_generate_class_with_aggregation(self):
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
                            name="Container",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Item",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="contains",
                            type=RelationType.AGGREGATION,
                            client="Container",
                            supplier="Item",
                        )
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            container_class = project.packages[0].classes[0]
            relations = [project.packages[0].dependencies[0]]
            code = manager.generate_class(container_class, relations)

            assert "items: list[Item] | None = None" in code
            assert "self._items = items or []" in code

    def test_generate_class_with_composition(self):
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
                            name="Parent",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Child",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="owns",
                            type=RelationType.COMPOSITION,
                            client="Parent",
                            supplier="Child",
                        )
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            parent_class = project.packages[0].classes[0]
            relations = [project.packages[0].dependencies[0]]
            code = manager.generate_class(parent_class, relations)

            assert "self._child = Child()" in code or "self._child" in code
            assert "child:" not in code or "def __init__(self):" in code

    def test_generate_class_with_generalization(self):
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
                            name="Base",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Derived",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="extends",
                            type=RelationType.GENERALIZATION,
                            client="Derived",
                            supplier="Base",
                        )
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            derived_class = project.packages[0].classes[1]
            relations = [project.packages[0].dependencies[0]]
            code = manager.generate_class(derived_class, relations)

            assert "class Derived(Base):" in code
            assert "from" in code  # Should import Base

    def test_generate_class_with_realization(self):
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
                            name="Interface",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Implementation",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="implements",
                            type=RelationType.REALIZATION,
                            client="Implementation",
                            supplier="Interface",
                        )
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            impl_class = project.packages[0].classes[1]
            relations = [project.packages[0].dependencies[0]]
            code = manager.generate_class(impl_class, relations)

            assert "class Implementation(Interface):" in code

    def test_generate_class_with_dependency(self):
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
                            name="Client",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Service",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="depends_on",
                            type=RelationType.DEPENDENCY,
                            client="Client",
                            supplier="Service",
                        )
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            client_class = project.packages[0].classes[0]
            relations = [project.packages[0].dependencies[0]]
            code = manager.generate_class(client_class, relations)

            assert "service:" not in code or "def __init__(self):" in code

    def test_generate_class_with_operations(self):
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
                            name="TestClass",
                            properties=[],
                            operations=[
                                Operation(
                                    id="o1",
                                    name="do_something",
                                    parameters=[
                                        Parameter(
                                            id="p1",
                                            name="value",
                                            type="String",
                                            direction=ParameterDirection.IN,
                                        )
                                    ],
                                    visibility=Visibility.PUBLIC,
                                ),
                                Operation(
                                    id="o2",
                                    name="get_result",
                                    parameters=[
                                        Parameter(
                                            id="p2",
                                            name="result",
                                            type="Integer",
                                            direction=ParameterDirection.RETURN,
                                        )
                                    ],
                                    visibility=Visibility.PUBLIC,
                                ),
                            ],
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
            manager = TemplateManager(project, output_dir)

            class_syntax = project.packages[0].classes[0]
            code = manager.generate_class(class_syntax, [])

            assert "def do_something(self, value: str) -> None:" in code
            assert "def get_result(self) -> int:" in code

    def test_generate_empty_class(self):
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
                            name="EmptyClass",
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
            manager = TemplateManager(project, output_dir)

            class_syntax = project.packages[0].classes[0]
            code = manager.generate_class(class_syntax, [])

            assert "class EmptyClass:" in code
            assert "pass" in code

    def test_generate_class_with_standard_types(self):
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
                            name="TestClass",
                            properties=[
                                Property(
                                    id="p1",
                                    name="id",
                                    type="String",
                                    visibility=Visibility.PRIVATE,
                                ),
                                Property(
                                    id="p2",
                                    name="count",
                                    type="Integer",
                                    visibility=Visibility.PRIVATE,
                                ),
                                Property(
                                    id="p3",
                                    name="price",
                                    type="Float",
                                    visibility=Visibility.PRIVATE,
                                ),
                            ],
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
            manager = TemplateManager(project, output_dir)

            class_syntax = project.packages[0].classes[0]
            code = manager.generate_class(class_syntax, [])

            assert "id: str" in code
            assert "count: int" in code
            assert "price: float" in code

    def test_generate_class_with_multiple_relations_same_type(self):
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
                            name="Client",
                            properties=[],
                            operations=[],
                        ),
                        Class(
                            id="c2",
                            name="Service",
                            properties=[],
                            operations=[],
                        ),
                    ],
                    dependencies=[
                        Relation(
                            id="r1",
                            name="uses1",
                            type=RelationType.ASSOCIATION,
                            client="Client",
                            supplier="Service",
                        ),
                        Relation(
                            id="r2",
                            name="uses2",
                            type=RelationType.ASSOCIATION,
                            client="Client",
                            supplier="Service",
                        ),
                    ],
                    data_types=[],
                )
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            manager = TemplateManager(project, output_dir)

            client_class = project.packages[0].classes[0]
            relations = project.packages[0].dependencies
            code = manager.generate_class(client_class, relations)

            assert "service: Service | None = None" in code
            assert "service1: Service | None = None" in code
            assert "self._service = service" in code
            assert "self._service1 = service1" in code
