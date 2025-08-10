from pathlib import Path

from src.ProjectGenerator import ProjectGenerator
from src.XmiParser import XmiParser


class Main:
    def __init__(self, xmi_path: Path, output_dir: Path) -> None:
        parsed_project = XmiParser.parse(xmi_path)
        ProjectGenerator.generate_project(parsed_project, output_dir)
