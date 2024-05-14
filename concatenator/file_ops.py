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


def validate_output_path(filepath: str, overwrite: bool = False) -> Path:
    """Checks whether an output path is a valid file and whether it already exists."""
    path = Path(filepath).resolve()
    if path.is_file():  # the file already exists
        if overwrite:
            os.remove(path)
        else:
            raise FileExistsError(
                f"File already exists at <{path}>. Run again with option '-O' to overwrite."
            )
    if path.is_dir():  # the specified path is an existing directory
        raise TypeError("Output path cannot be a directory. Please specify a new filepath.")
    return path


def validate_input_path(path_or_paths: list[str]) -> list[str]:
    """Checks whether input is a valid directory, list of files, or a text file containing paths."""
    print(f"parsed_input === {path_or_paths}")
    if len(path_or_paths) > 1:
        input_files = path_or_paths
    elif len(path_or_paths) == 1:
        directory_or_path = Path(path_or_paths[0]).resolve()
        if directory_or_path.is_dir():
            input_files = _get_list_of_filepaths_from_dir(directory_or_path)
        elif directory_or_path.is_file():
            input_files = _get_list_of_filepaths_from_file(directory_or_path)
        else:
            raise TypeError(
                "If one path is provided for 'data_dir_or_file_or_filepaths', "
                "then it must be an existing directory or file."
            )
    else:
        raise TypeError("input argument must be one path/directory or a list of paths.")
    return input_files


def _get_list_of_filepaths_from_file(file_with_paths: Path) -> list[str]:
    """Each path listed in the specified file is resolved using pathlib for validation."""
    paths_list = []
    with open(file_with_paths, encoding="utf-8") as file:
        while line := file.readline():
            paths_list.append(str(Path(line.rstrip()).resolve()))

    return paths_list


def _get_list_of_filepaths_from_dir(data_dir: Path) -> list[str]:
    """Get a list of files (ignoring hidden files) in directory."""
    input_files = [str(f) for f in data_dir.iterdir() if not f.name.startswith(".")]
    return input_files
