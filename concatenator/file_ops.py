"""File operation functions."""

from __future__ import annotations

import logging
import os
from logging import Logger
from pathlib import Path

import netCDF4 as nc
import numpy as np

module_logger = logging.getLogger(__name__)

netcdf_extensions = [".nc", ".nc4", ".netcdf"]


def validate_output_path(filepath: str, overwrite: bool = False) -> str:
    """Checks whether an output path is a valid file and whether it already exists."""
    path = Path(filepath).resolve()
    if path.is_file():  # the file already exists
        if overwrite:
            os.remove(path)
        else:
            raise FileExistsError(
                f"File already exists at <{path}>. "
                f"Run again with `overwrite` option to overwrite existing file."
            )
    if path.is_dir():  # the specified path is an existing directory
        raise TypeError("Output path cannot be a directory. Please specify a new filepath.")
    return str(path)


def validate_input_path(path_or_paths: list[str]) -> list[str]:
    """Checks whether input is a list of files, a directory, or a text file containing paths.

    If the input is...
    - a list of filepaths, then use those filepaths.
    - a valid directory, then get the paths for all the files in the directory.
    - a single file:
        - that is a valid text file, then get the names of the files from each row in the text file.
        - that is a valid netCDF file, then use that one filepath
    """
    print(f"parsed_input === {path_or_paths}")
    if len(path_or_paths) > 1:
        input_files = path_or_paths
    elif len(path_or_paths) == 1:
        directory_or_path = Path(path_or_paths[0]).resolve()
        if directory_or_path.is_dir():
            input_files = _get_list_of_filepaths_from_dir(directory_or_path)
        elif directory_or_path.is_file():
            if directory_or_path.suffix in netcdf_extensions:
                input_files = [str(directory_or_path)]
            else:
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


def validate_workable_files(
    files: list[str], logger: Logger | None = module_logger
) -> tuple[list[str], int]:
    """Remove files from a list that are not open-able as netCDF or that are empty."""
    workable_files = []
    for file in files:
        try:
            with nc.Dataset(file, "r") as dataset:
                is_empty = _is_file_empty(dataset)
                if is_empty is False:
                    workable_files.append(file)
        except OSError:
            if logger:
                logger.debug("Error opening <%s> as a netCDF dataset. Skipping.", file)
            else:
                print("Error opening <%s> as a netCDF dataset. Skipping.")

    # addressing GitHub issue 153: propagate the first empty file if all input files are empty
    if (len(workable_files) == 0) and (len(files) > 0):
        workable_files.append(files[0])

    number_of_workable_files = len(workable_files)

    return workable_files, number_of_workable_files


def _is_file_empty(parent_group: nc.Dataset | nc.Group) -> bool:
    """Check if netCDF dataset is empty or not.

    Tests if all variable arrays are empty.
    As soon as a variable is detected with both (i) an array size not equal to zero and
    (ii) not all null/fill values, then the granule is considered non-empty.

    Returns
    -------
    False if the dataset is considered non-empty; True otherwise (dataset is indeed empty).
    """
    for var_name, var in parent_group.variables.items():
        if var.size != 0:
            if "_FillValue" in var.ncattrs():
                fill_or_null = getattr(var, "_FillValue")
            else:
                fill_or_null = np.nan

            # This checks three ways that the variable's array might be considered empty.
            # If none of the ways are true,
            #   a non-empty variable has been found and False is returned.
            # If one of the ways is true, we consider the variable empty,
            #   and continue checking other variables.
            empty_way_1 = False
            if np.ma.isMaskedArray(var[:]):
                empty_way_1 = var[:].mask.all()
            empty_way_2 = np.all(var[:].data == fill_or_null)
            empty_way_3 = np.all(np.isnan(var[:].data))

            if not (empty_way_1 or empty_way_2 or empty_way_3):
                return False  # Found a non-empty variable.

    for child_group in parent_group.groups.values():
        return _is_file_empty(child_group)
    return True
