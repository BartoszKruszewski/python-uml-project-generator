from pathlib import Path
from pprint import pprint

from XmiParser import XmiParser


class Main:
    def __init__(self, xmi_path: Path, output_dir: Path) -> None:
        parsed_project = XmiParser.parse(xmi_path)
        pprint(parsed_project, indent=0, compact=True,)
