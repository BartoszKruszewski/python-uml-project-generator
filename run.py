import argparse
import logging
from pathlib import Path

from src.Main import Main


def validate_xmi_path(input: str) -> Path:
    xmi_path = Path(input)
    if not xmi_path.exists():
        raise argparse.ArgumentTypeError(f"XMI path: {xmi_path} not exists!")
    return xmi_path


def validate_output_dir(input: str) -> Path:
    output_dir = Path(input)
    if output_dir.exists() and output_dir.is_file():
        raise argparse.ArgumentTypeError(f"Output dir: {output_dir} is not a dir!")
    output_dir.mkdir(exist_ok=True, parents=True)
    return output_dir


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Nice description")
    parser.add_argument("xmi_path", type=validate_xmi_path, help="Path to XMI file")
    parser.add_argument('output_dir', type=validate_output_dir, help='Output dir')
    args = parser.parse_args()
    Main(xmi_path=args.xmi_path, output_dir=args.output_dir)
