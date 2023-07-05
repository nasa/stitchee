"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""

import logging
import time
from logging import Logger
from pathlib import Path

import netCDF4 as nc  # type: ignore
import xarray as xr

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

    def _label_filename_as_intermediate(x: str) -> str:
        pathlib_x = Path(x)
        return str(pathlib_x.parent / f"{pathlib_x.stem}_flat_intermediate{pathlib_x.suffix}")

    num_files = len(files_to_concat)
    logger.debug("Flattening all input files...")
    for i, filepath in enumerate(files_to_concat):
        # The group structure is flattened.
        start_time = time.time()
        logger.debug("    ..file %03d/%d <%s>..", i, num_files, filepath)
        flat_dataset, coord_vars, string_vars = flatten_grouped_dataset(nc.Dataset(filepath, 'r'), filepath,
                                                                        ensure_all_dims_are_coords=True)
        xrds = xr.open_dataset(xr.backends.NetCDF4DataStore(flat_dataset),
                               decode_times=False, decode_coords=False, drop_variables=coord_vars)
        benchmark_log['flattening'] = time.time() - start_time

        # The flattened file is written to disk.
        flat_file_path = _label_filename_as_intermediate(filepath)
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
    combined_ds.to_netcdf(_label_filename_as_intermediate(output_file))

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