from pathlib import Path
from pprint import pprint

from project_generator.ProjectGenerator import ProjectGenerator
from project_generator.XmiParser import XmiParser


def generate_project(xmi_path: Path, output_dir: Path) -> None:
    """Main function to generate a project from an XMI file.

    Args:
        xmi_path: Path to the XMI file.
        output_dir: Path to the output directory where the project will be generated.
    """
    print(xmi_path.read_text())
    parsed_project = XmiParser.parse(xmi_path)
    pprint(parsed_project)
    ProjectGenerator(parsed_project, output_dir)
