"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""

import logging
import time
from logging import Logger
from typing import Union

import netCDF4 as nc  # type: ignore
import xarray as xr

from concatenator.file_ops import add_label_to_path
from concatenator.group_handling import (flatten_grouped_dataset,
                                         regroup_flattened_dataset)

default_logger = logging.getLogger(__name__)


def bumblebee(files_to_concat: list[str],
              output_file: str,
              logger: Logger = default_logger) -> str:
    """Concatenate netCDF data files along an existing dimension.

    Parameters
    ----------
    files_to_concat : list[str]
    output_file : str
    logger : logging.Logger

    Returns
    -------
    str
    """
    intermediate_flat_filepaths: list[str] = []
    benchmark_log = {"flattening": 0.0, "concatenating": 0.0, "reconstructing_groups": 0.0}

    # Only concatenate files that are not empty.
    input_files = []
    for file in files_to_concat:
        try:
            with nc.Dataset(file, 'r') as dataset:
                is_empty = _is_file_empty(dataset)
                if is_empty is False:
                    input_files.append(file)
        except OSError:
            logger.debug("Error opening <%s> as a netCDF dataset. Skipping.", file)

    # Exit cleanly if no workable netCDF files found.
    num_files = len(input_files)
    if num_files < 1:
        logger.info("No non-empty netCDF files found. Exiting.")
        return ""

    logger.debug("Flattening all input files...")
    for i, filepath in enumerate(input_files):
        # The group structure is flattened.
        start_time = time.time()
        logger.debug("    ..file %03d/%03d <%s>..", i + 1, num_files, filepath)
        flat_dataset, coord_vars, string_vars = flatten_grouped_dataset(nc.Dataset(filepath, 'r'), filepath,
                                                                        ensure_all_dims_are_coords=True)
        xrds = xr.open_dataset(xr.backends.NetCDF4DataStore(flat_dataset),
                               decode_times=False, decode_coords=False, drop_variables=coord_vars)
        benchmark_log['flattening'] = time.time() - start_time

        # The flattened file is written to disk.
        flat_file_path = add_label_to_path(filepath, label="_flat_intermediate")
        xrds.to_netcdf(flat_file_path, encoding={v_name: {'dtype': 'str'} for v_name in string_vars})
        intermediate_flat_filepaths.append(flat_file_path)

    # Flattened files are concatenated together (Using XARRAY).
    start_time = time.time()
    logger.debug("Concatenating flattened files...")
    combined_ds = xr.open_mfdataset(intermediate_flat_filepaths,
                                    decode_times=False,
                                    decode_coords=False,
                                    data_vars='minimal',
                                    coords='minimal',
                                    compat='override')
    benchmark_log['concatenating'] = time.time() - start_time

    # Concatenated, yet still flat, file is written to disk for debugging.
    combined_ds.to_netcdf(add_label_to_path(output_file, label="_flat_intermediate"))

    # The group hierarchy of the concatenated file is reconstructed (using XARRAY).
    start_time = time.time()
    logger.debug("Reconstructing groups within concatenated file...")
    regroup_flattened_dataset(combined_ds, output_file)
    benchmark_log['reconstructing_groups'] = time.time() - start_time

    print("--- Benchmark results ---")
    total_time = 0.0
    for k, v in benchmark_log.items():
        logger.info("%s: %f", k, v)
        total_time += v
    logger.info("-- total time: %f", total_time)

    return output_file


def _is_file_empty(parent_group: Union[nc.Dataset, nc.Group]) -> bool:
    """
    Function to test if a all variable size in a dataset is 0
    """
    for var in parent_group.variables.values():
        if var.size != 0:
            return False
    for child_group in parent_group.groups.values():
        return _is_file_empty(child_group)
    return True
