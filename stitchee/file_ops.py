"""File operation functions."""

from __future__ import annotations

import logging
import os
from logging import Logger
from pathlib import Path

import netCDF4 as nc
import numpy as np

module_logger = logging.getLogger(__name__)

# Module constants
NETCDF_EXTENSIONS = [".nc", ".nc4", ".netcdf"]


def validate_output_path(filepath: str, overwrite: bool = False) -> str:
    """Validate output path and handle overwrite option.

    Returns
    -------
    str
        Resolved output file path
    """
    path = Path(filepath).resolve()

    if path.is_dir():
        raise TypeError(f"Output path '{path}' is a directory. Please specify a file path.")

    if path.is_file() and not overwrite:
        raise FileExistsError(f"File already exists at <{path}>. Use overwrite=True to replace it.")

    if path.is_file() and overwrite:
        os.remove(path)

    return str(path)


def validate_input_path(path_or_paths: list[str]) -> list[str]:
    """Process input path(s) into a list of file paths.

    Handles:
    - List of file paths
    - Directory path (returns all files in directory)
    - Single netCDF file
    - Text file containing paths (one per line)

    Parameters
    ----------
    path_or_paths
        One or more input paths

    Returns
    -------
    list[str]
        List of resolved file paths

    Raises
    ------
    ValueError
        If input path(s) cannot be resolved
    """
    module_logger.debug("Validating input paths: %s", path_or_paths)

    if not path_or_paths:
        raise ValueError("No input paths provided")

    # Multiple paths provided
    if len(path_or_paths) > 1:
        return [str(Path(p).resolve()) for p in path_or_paths]

    # Single path - could be file or directory
    path = Path(path_or_paths[0]).resolve()

    if path.is_dir():
        return _get_list_of_filepaths_from_dir(path)

    if path.is_file():
        if path.suffix.lower() in NETCDF_EXTENSIONS:
            return [str(path)]
        else:
            return _get_list_of_filepaths_from_file(path)

    raise ValueError(f"Input path '{path}' is not a valid file or directory")


def validate_workable_files(
    files: list[str], logger: Logger = module_logger
) -> tuple[list[str], int]:
    """Filter input files to those that are valid non-empty netCDF files.

    Returns
    -------
    tuple[list[str], int]
        List of workable files and the count

    Notes
    -----
    If all input files are empty, the first file will be returned
    to maintain compatibility with downstream processes.
    """
    workable_files = []
    for file in files:
        try:
            with nc.Dataset(file, "r") as dataset:
                if not _is_file_empty(dataset):
                    workable_files.append(file)
                    logger.debug("File is valid and non-empty: %s", file)
                else:
                    logger.debug("File is empty: %s", file)

        except Exception as e:
            logger.debug("Error opening %s as netCDF: %s", file, e)

    return workable_files, len(workable_files)


def _get_list_of_filepaths_from_dir(data_dir: Path) -> list[str]:
    """Get list of files (ignoring hidden files) in directory."""
    module_logger.debug("Getting files from directory: %s", data_dir)

    # Filter out hidden files and return absolute paths
    files = [
        str(f.resolve()) for f in data_dir.iterdir() if f.is_file() and not f.name.startswith(".")
    ]

    if not files:
        module_logger.warning("No files found in directory: %s", data_dir)

    return files


def _get_list_of_filepaths_from_file(file_with_paths: Path) -> list[str]:
    """Extract file paths from a text file, one path per line."""
    module_logger.debug("Reading paths from file: %s", file_with_paths)

    paths = []
    try:
        with open(file_with_paths, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Skip empty lines and comments
                    paths.append(str(Path(line).resolve()))
    except Exception as e:
        raise ValueError(f"Failed to read paths from {file_with_paths}: {e}")

    return paths


def _is_file_empty(parent_group: nc.Dataset | nc.Group) -> bool:
    """Check if netCDF dataset is empty.

    A dataset is considered empty if all variables are:
    1. Zero size, OR
    2. All masked values (for masked arrays), OR
    3. All fill values, OR
    4. All NaN values

    Parameters
    ----------
    parent_group
        netCDF dataset or group to check

    Returns
    -------
    bool
        True if dataset is empty, False if any variable contains data
    """
    for var_name, var in parent_group.variables.items():
        if var.size == 0:
            continue  # Empty variable, check next one

        # Get fill value if defined
        fill_or_null = (
            getattr(var, "_FillValue", np.nan) if "_FillValue" in var.ncattrs() else np.nan
        )

        # Load the data
        var_data = var[:]

        # Check if variable is non-empty using three different methods
        if np.ma.isMaskedArray(var_data):
            # Check 1: Are all values masked?
            if not var_data.mask.all() and not np.all(np.isnan(var_data.data)):
                return False  # Found a non-empty masked array

        # Check 2: Are all values equal to fill value?
        # Check 3: Are all values NaN?
        if not np.all(var_data.data == fill_or_null) and not np.all(np.isnan(var_data.data)):
            return False  # Found a non-empty variable

    # Check all child groups recursively
    for child_group in parent_group.groups.values():
        if not _is_file_empty(child_group):
            return False  # Found non-empty child group

    return True  # All variables and groups are empty
