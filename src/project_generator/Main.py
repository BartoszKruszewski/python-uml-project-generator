from pathlib import Path
from pprint import pprint

from project_generator.ProjectGenerator import ProjectGenerator
from project_generator.XmiParser import XmiParser


class Main:
    def __init__(self, xmi_path: Path, output_dir: Path) -> None:
        parsed_project = XmiParser.parse(xmi_path)
        pprint(parsed_project)
        ProjectGenerator(parsed_project, output_dir)
