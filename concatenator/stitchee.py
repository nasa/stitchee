"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""

from __future__ import annotations

import logging
import shutil
import time
from functools import partial
from logging import Logger
from warnings import warn

import xarray as xr

from concatenator.file_ops import (
    validate_input_path,
    validate_output_path,
    validate_workable_files,
)

default_logger = logging.getLogger(__name__)


def stitchee(
    files_to_concat: list[str],
    output_file: str,
    concat_method: str = "xarray-concat",
    concat_dim: str = "",
    concat_kwargs: dict | None = None,
    sorting_variable: str | None = None,
    history_to_append: str | None = None,
    overwrite_output_file: bool = False,
    logger: Logger = default_logger,
) -> str:
    """Concatenate netCDF data files along an existing dimension.

    Parameters
    ----------
    files_to_concat
        netCDF files to concatenate
    output_file
        file path for output file
    concat_method
        concatenation method, either "xarray-concat" (default) or "xarray-combine".
    concat_dim
        dimension along which to concatenate (default: "").
        Not needed if concat_method is "xarray-combine".
    concat_kwargs
        keyword arguments to pass to xarray.concat or xarray.combine_by_coords (default: None).
    sorting_variable
        name of a variable to use for sorting datasets before concatenation (e.g., `time`).
    history_to_append
        JSON string to append to the history attribute of the concatenated file (default: None).
    overwrite_output_file
        whether to overwrite output file if it exists (default: False).
    logger
        logger instance for output messages

    Returns
    -------
    str
        path of concatenated file, empty string if no workable files found

    Raises
    ------
    ValueError
        If concat_method or concat_dim are invalid
    KeyError
        If datatrees have mismatched dataset nodes or sorting variable is not found
    """
    if not files_to_concat:
        raise ValueError("files_to_concat cannot be empty")
    validate_input_path(files_to_concat)
    concat_kwargs = concat_kwargs or {}

    _validate_concat_method_and_dim(concat_dim, concat_method)

    # Get workable files (those that can be opened and are not empty).
    input_files, num_input_files = validate_workable_files(files_to_concat, logger)

    # Handle zero files case: exit cleanly.
    if num_input_files < 1:
        logger.info("No non-empty netCDF files found. Exiting.")
        return ""

    output_file = validate_output_path(output_file, overwrite=overwrite_output_file)

    # Handle single file case: exit cleanly with the file copied.
    if num_input_files == 1:
        shutil.copyfile(input_files[0], output_file)
        logger.info("One workable netCDF file. Copied to output path without modification.")
        return output_file

    # Process multiple files.
    start_time = time.time()

    try:
        datatree_list = _load_and_sort_datatrees(input_files, sorting_variable, logger)

        logger.info("Concatenating files...")
        output_tree = _concatenate_datatrees(
            datatree_list, concat_method, concat_dim, concat_kwargs
        )

        _finalize_output(output_tree, output_file, history_to_append)

        logger.info("Total processing time: %.2f seconds", time.time() - start_time)

    except Exception as err:
        logger.error("Stitchee encountered an error: %s", str(err))
        raise

    return output_file


def _validate_concat_method_and_dim(concat_dim: str, concat_method: str) -> None:
    """Validate concatenation method and warn if concat_dim won't be used."""
    if concat_method not in ("xarray-concat", "xarray-combine"):
        raise ValueError(f"Unexpected concatenation method: {concat_method}")

    if concat_method == "xarray-concat" and not concat_dim:
        raise ValueError("concat_dim is required when using 'xarray-concat' method")

    if concat_dim and (concat_method == "xarray-combine"):
        warn(
            "'concat_dim' was specified but will not be used "
            "because 'xarray-combine' method was selected."
        )


def _load_and_sort_datatrees(
    input_files: list[str], sorting_variable: str | None, logger: Logger
) -> list[xr.DataTree]:
    """Load datatrees while validating consistency, and return trees in a sorted list."""
    datatree_list = []
    sort_values = []
    first_keys = None

    for i, filepath in enumerate(input_files):
        logger.info("Processing file %03d/%03d <%s>", i + 1, len(input_files), filepath)

        # Open data file and add to the datatree list.
        datatree = xr.open_datatree(
            filepath,
            decode_times=False,
            decode_coords=False,
            mask_and_scale=False,
        )

        # Check dataset node consistency immediately
        current_keys = set(datatree.to_dict().keys())
        if first_keys is None:
            first_keys = current_keys
        elif current_keys != first_keys:
            mismatched = current_keys ^ first_keys
            raise KeyError(
                f"Mismatched dataset nodes. In file {i + 1} ({filepath}), "
                f"expected keys: {sorted(first_keys)}, got: {sorted(current_keys)}. "
                f"Differences: {sorted(mismatched)}"
            )

        datatree_list.append(datatree)

        # Validate and extract sorting value.
        if sorting_variable:
            try:
                sort_value = datatree[sorting_variable].values.flatten()[0]
            except Exception as err:
                logger.error(
                    f"Cannot extract sorting value from '{sorting_variable}' in {filepath}: {err}"
                )
                raise
        else:
            sort_value = i

        sort_values.append(sort_value)

    # Reorder the datatrees according to the sorting key values.
    sorted_pairs = sorted(zip(sort_values, datatree_list), key=lambda x: x[0])
    datatree_list = [datatree for _, datatree in sorted_pairs]
    return datatree_list


def _concatenate_datatrees(
    datatree_list: list[xr.DataTree], concat_method: str, concat_dim: str, concat_kwargs: dict
) -> xr.DataTree:
    """Concatenate the datatrees using the specified method."""
    if not datatree_list:  # Add this check
        raise ValueError("Cannot concatenate empty list of datatrees")

    concat_func = {
        "xarray-concat": partial(xr.concat, dim=concat_dim),
        "xarray-combine": xr.combine_by_coords,
    }.get(concat_method)

    if concat_func is None:
        raise ValueError(f"Unexpected concatenation method: {concat_method}")

    tree_dicts = [tree.to_dict() for tree in datatree_list]
    first_keys = set(tree_dicts[0].keys())

    return xr.DataTree.from_dict(
        {
            key: concat_func(
                [td[key] for td in tree_dicts],
                data_vars="minimal",
                coords="minimal",
                **concat_kwargs,
            )
            for key in first_keys
        }
    )


def _finalize_output(
    output_tree: xr.DataTree, output_file: str, history_to_append: str | None
) -> None:
    """Add history and save the output tree."""
    if history_to_append is not None:
        output_tree.attrs["history_json"] = history_to_append
    output_tree.to_netcdf(output_file)

    # new_global_attributes = create_new_attributes(combined_ds, request_parameters=dict())
