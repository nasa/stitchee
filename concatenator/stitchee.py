"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""

from __future__ import annotations

import logging
import shutil
import time
from logging import Logger
from warnings import warn

import xarray as xr

import concatenator
from concatenator.dataset_and_group_handling import validate_workable_files
from concatenator.file_ops import (
    validate_input_path,
    validate_output_path,
)

default_logger = logging.getLogger(__name__)


def stitchee(
    files_to_concat: list[str],
    output_file: str,
    concat_method: str | None = "xarray-concat",
    concat_dim: str = "",
    concat_kwargs: dict | None = None,
    sorting_variable: str | None = None,
    history_to_append: str | None = None,
    overwrite_output_file: bool = False,
    group_delimiter: str = "__",
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
        either "xarray-concat" (default) or "xarray-combine".
    concat_dim
        dimension along which to concatenate (default: "").
        Not needed if concat_method is "xarray-combine".
    concat_kwargs
        keyword arguments to pass to xarray.concat or xarray.combine_by_coords (default: None).
    sorting_variable
        name of a variable to use for sorting datasets before concatenation by xarray.
        E.g., `time`.
    history_to_append
        JSON string to append to the history attribute of the concatenated file (default: None).
    overwrite_output_file
        whether to overwrite output file (default: False).
    group_delimiter
        character used to separate groups (default: "__").
    logger

    Returns
    -------
    str
        path of concatenated file
    """
    validate_input_path(files_to_concat)
    concatenator.group_delim = group_delimiter

    benchmark_log = {
        "concatenating": 0.0,
    }

    # Proceed to concatenate only files that are workable (can be opened and are not empty).
    input_files, num_input_files = validate_workable_files(files_to_concat, logger)

    # Exit cleanly if no workable netCDF files found.
    if num_input_files < 1:
        logger.info("No non-empty netCDF files found. Exiting.")
        return ""

    output_file = validate_output_path(output_file, overwrite=overwrite_output_file)

    # Exit cleanly with the file copied if one workable netCDF file found.
    if num_input_files == 1:
        shutil.copyfile(input_files[0], output_file)
        logger.info("One workable netCDF file. Copied to output path without modification.")
        return output_file

    if concat_dim and (concat_method == "xarray-combine"):
        warn(
            "'concat_dim' was specified, but will not be used because xarray-combine method was "
            "selected."
        )

    try:
        xrdatatree_list = []
        concat_dim_order = []
        for i, filepath in enumerate(input_files):
            # The group structure is flattened.
            start_time = time.time()
            logger.info("    ..file %03d/%03d <%s>..", i + 1, num_input_files, filepath)

            logger.info("Opening flattened file with xarray.")
            datatree = xr.open_datatree(
                filepath,
                decode_times=False,
                decode_coords=False,
                mask_and_scale=False,
            )

            # Determine value for later dataset sorting.
            if sorting_variable:
                first_value = datatree[sorting_variable].values.flatten()[0]
            else:
                first_value = i
            # first_value = xrds[concatenator.group_delim + concat_dim].values.flatten()[0]
            concat_dim_order.append(first_value)

            xrdatatree_list.append(datatree)

        # Reorder the xarray datasets according to the concat dim values.
        xrdatatree_list = [
            datatree
            for _, datatree in sorted(zip(concat_dim_order, xrdatatree_list), key=lambda x: x[0])
        ]

        tree_dicts = [tree.to_dict() for tree in xrdatatree_list]
        keys_list = [set(t.keys()) for t in tree_dicts]
        symmetric_diff = any([kl ^ keys_list[0] for kl in keys_list])

        if symmetric_diff:
            raise KeyError(
                f"Datatrees do not have matching Dataset nodes. Nodes that do not match: {symmetric_diff}."
            )

        # Files are concatenated together (Using XARRAY).
        start_time = time.time()
        logger.info("Concatenating files...")
        # combined_ds = xr.open_mfdataset(intermediate_flat_filepaths,
        #                                 decode_times=False,
        #                                 decode_coords=False,
        #                                 data_vars='minimal',
        #                                 coords='minimal',
        #                                 compat='override')

        if concat_kwargs is None:
            concat_kwargs = {}

        tree_keys = keys_list[0]

        if concat_method == "xarray-concat":
            combined_dict = {
                kk: xr.concat(
                    [tree_dict[kk] for tree_dict in tree_dicts],
                    data_vars="minimal",
                    coords="minimal",
                    **concat_kwargs,
                    dim=concat_dim,
                )
                for kk in tree_keys
            }

        elif concat_method == "xarray-combine":
            combined_dict = {
                kk: xr.combine_by_coords(
                    [tree_dict[kk] for tree_dict in tree_dicts],
                    data_vars="minimal",
                    coords="minimal",
                    **concat_kwargs,
                    dim=concat_dim,
                )
                for kk in tree_keys
            }
        else:
            raise ValueError(f"Unexpected concatenation method, <{concat_method}>.")

        output_dt = xr.DataTree.from_dict(combined_dict)
        if history_to_append is not None:
            output_dt.attrs["history_json"] = history_to_append
        output_dt.to_netcdf(output_file)

        benchmark_log["concatenating"] = time.time() - start_time

        # new_global_attributes = create_new_attributes(combined_ds, request_parameters=dict())

        # The group hierarchy of the concatenated file is reconstructed (using XARRAY).
        start_time = time.time()

        logger.info("--- Benchmark results ---")
        total_time = 0.0
        for k, v in benchmark_log.items():
            logger.info("%s: %f", k, v)
            total_time += v
        logger.info("-- total processing time: %f", total_time)

    except Exception as err:
        logger.info("Stitchee encountered an error!")
        logger.error(err)
        raise err

    return output_file
