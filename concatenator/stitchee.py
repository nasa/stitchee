"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""
import logging
import os
import time
from logging import Logger

import netCDF4 as nc
import xarray as xr

from concatenator import GROUP_DELIM
from concatenator.dimension_cleanup import remove_duplicate_dims
from concatenator.file_ops import add_label_to_path
from concatenator.group_handling import (
    flatten_grouped_dataset,
    regroup_flattened_dataset,
)

default_logger = logging.getLogger(__name__)


def stitchee(
    files_to_concat: list[str],
    output_file: str,
    write_tmp_flat_concatenated: bool = False,
    keep_tmp_files: bool = True,
    concat_dim: str = "",
    logger: Logger = default_logger,
) -> str:
    """Concatenate netCDF data files along an existing dimension.

    Parameters
    ----------
    files_to_concat : list[str]
    output_file : str
    keep_tmp_files : bool
    concat_dim : str, optional
    logger : logging.Logger

    Returns
    -------
    str
    """
    intermediate_flat_filepaths: list[str] = []
    benchmark_log = {"flattening": 0.0, "concatenating": 0.0, "reconstructing_groups": 0.0}

    # Proceed to concatenate only files that are workable (can be opened and are not empty).
    input_files, num_input_files = _validate_workable_files(files_to_concat, logger)

    # Exit cleanly if no workable netCDF files found.
    if num_input_files < 1:
        logger.info("No non-empty netCDF files found. Exiting.")
        return ""

    logger.debug("Flattening all input files...")
    xrdataset_list = []
    for i, filepath in enumerate(input_files):
        # The group structure is flattened.
        start_time = time.time()
        logger.debug("    ..file %03d/%03d <%s>..", i + 1, num_input_files, filepath)
        flat_dataset, coord_vars, _ = flatten_grouped_dataset(
            nc.Dataset(filepath, "r"), filepath, ensure_all_dims_are_coords=True
        )

        flat_dataset = remove_duplicate_dims(flat_dataset)

        xrds = xr.open_dataset(
            xr.backends.NetCDF4DataStore(flat_dataset),
            decode_times=False,
            decode_coords=False,
            drop_variables=coord_vars,
        )

        benchmark_log["flattening"] = time.time() - start_time

        # The flattened file is written to disk.
        # flat_file_path = add_label_to_path(filepath, label="_flat_intermediate")
        # xrds.to_netcdf(flat_file_path, encoding={v_name: {'dtype': 'str'} for v_name in string_vars})
        # intermediate_flat_filepaths.append(flat_file_path)
        # xrdataset_list.append(xr.open_dataset(flat_file_path))
        xrdataset_list.append(xrds)

    # Flattened files are concatenated together (Using XARRAY).
    start_time = time.time()
    logger.debug("Concatenating flattened files...")
    # combined_ds = xr.open_mfdataset(intermediate_flat_filepaths,
    #                                 decode_times=False,
    #                                 decode_coords=False,
    #                                 data_vars='minimal',
    #                                 coords='minimal',
    #                                 compat='override')

    combined_ds = xr.concat(
        xrdataset_list, dim=GROUP_DELIM + concat_dim, data_vars="minimal", coords="minimal"
    )

    benchmark_log["concatenating"] = time.time() - start_time

    if write_tmp_flat_concatenated:
        logger.debug("Writing concatenated flattened temporary file to disk...")
        # Concatenated, yet still flat, file is written to disk for debugging.
        tmp_flat_concatenated_path = add_label_to_path(output_file, label="_flat_intermediate")
        combined_ds.to_netcdf(tmp_flat_concatenated_path, format="NETCDF4")
    else:
        tmp_flat_concatenated_path = None

    # The group hierarchy of the concatenated file is reconstructed (using XARRAY).
    start_time = time.time()
    logger.debug("Reconstructing groups within concatenated file...")
    regroup_flattened_dataset(combined_ds, output_file)
    benchmark_log["reconstructing_groups"] = time.time() - start_time

    logger.info("--- Benchmark results ---")
    total_time = 0.0
    for k, v in benchmark_log.items():
        logger.info("%s: %f", k, v)
        total_time += v
    logger.info("-- total processing time: %f", total_time)

    # If requested, remove temporary intermediate files.
    if not keep_tmp_files:
        for file in intermediate_flat_filepaths:
            os.remove(file)
        if tmp_flat_concatenated_path:
            os.remove(tmp_flat_concatenated_path)

    return output_file


def _validate_workable_files(files_to_concat, logger) -> tuple[list[str], int]:
    """Remove files from list that are not open-able as netCDF or that are empty."""
    workable_files = []
    for file in files_to_concat:
        try:
            with nc.Dataset(file, "r") as dataset:
                is_empty = _is_file_empty(dataset)
                if is_empty is False:
                    workable_files.append(file)
        except OSError:
            logger.debug("Error opening <%s> as a netCDF dataset. Skipping.", file)

    number_of_workable_files = len(workable_files)

    return workable_files, number_of_workable_files


def _is_file_empty(parent_group: nc.Dataset | nc.Group) -> bool:
    """
    Function to test if a all variable size in a dataset is 0
    """
    for var in parent_group.variables.values():
        if var.size != 0:
            return False
    for child_group in parent_group.groups.values():
        return _is_file_empty(child_group)
    return True
