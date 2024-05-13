"""File operation functions."""

import logging
import os
import shutil
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


def add_label_to_path(x: str, label="_flat_intermediate") -> str:
    """Constructs new filepath with label at end."""
    pathlib_x = Path(x)
    return str(pathlib_x.parent / f"{pathlib_x.stem}{label}{pathlib_x.suffix}")


def make_temp_dir_with_input_file_copies(
    input_files: list[str], output_path: Path
) -> tuple[list[str], str]:
    """Creates temporary directory and copies input files."""
    new_data_dir = Path(
        add_label_to_path(str(output_path.parent / "temp_copy"), label=str(uuid.uuid4()))
    ).resolve()
    os.makedirs(new_data_dir, exist_ok=True)
    logger.info("Created temporary directory: %s", str(new_data_dir))

    new_input_files = []
    for file in input_files:
        new_path = new_data_dir / Path(file).name
        shutil.copyfile(file, new_path)
        new_input_files.append(str(new_path))

    input_files = new_input_files
    logger.info("Copied files to temporary directory: %s", new_data_dir)
    temporary_dir_to_remove = str(new_data_dir)

    return input_files, temporary_dir_to_remove
