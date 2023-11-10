"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""
import logging
import os
import time
from collections.abc import Generator
from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from warnings import warn

import h5py
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


@contextmanager
def open_netcdf_dataset_or_hdf_file(
    file_to_open: str | Path, mode="r"
) -> Generator[tuple[object, str], None, None]:
    print("entered the context manager")
    suffix = Path(file_to_open).suffix.lower()

    if suffix in [".nc", ".nc4", ".netcdf", ".netcdf4"]:
        managed_resource = nc.Dataset(file_to_open, mode)
        file_kind = "netcdf"
    elif suffix in [".h5", ".hdf", ".hdf5"]:
        managed_resource = h5py.File(file_to_open, mode)
        file_kind = "hdf"
    else:
        raise TypeError("Unexpected file extension, <%s>." % suffix)

    try:
        yield managed_resource, file_kind
    except BlockingIOError as err:
        print("File is already opened, and needs to be closed before trying this again.")
        raise err
    # except OSError:
    #     print("Could not open file in append mode using netCDF4. Trying h5py..")
    #     managed_resource = h5py.File(file_to_open, mode)
    #     yield managed_resource
    #     # any cleanup that should only be done on failure
    #     # raise
    except Exception:
        # print('caught:', e)
        raise
    else:
        # any cleanup that should only be done on success
        print("no exception was thrown")
    finally:
        # any cleanup that should always be done
        try:
            managed_resource.close()
        except Exception:
            print("Could not close the resource.")
        print("exited the context manager")


def stitchee(
    files_to_concat: list[str],
    output_file: str,
    write_tmp_flat_concatenated: bool = False,
    keep_tmp_files: bool = True,
    concat_method: str = "xarray-concat",
    concat_dim: str = "",
    concat_kwargs: dict | None = None,
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
    else:
        logger.info(f"{num_input_files} workable files identified.")

    if concat_dim and (concat_method == "xarray-combine"):
        warn(
            "'concat_dim' was specified, but will not be used because xarray-combine method was selected."
        )

    logger.info("Flattening all input files...")
    xrdataset_list = []

    try:
        for i, filepath in enumerate(input_files):
            # The group structure is flattened.
            start_time = time.time()
            logger.info("    ..file %03d/%03d <%s>..", i + 1, num_input_files, filepath)
            # ncds = nc.Dataset(filepath, "r")
            # ncds.close()

            with open_netcdf_dataset_or_hdf_file(filepath, "r+") as (nc_dataset, file_kind):
                flat_dataset, coord_vars, _ = flatten_grouped_dataset(
                    nc_dataset, ensure_all_dims_are_coords=True
                )

                logger.info("Removing duplicate dimensions")
                flat_dataset = remove_duplicate_dims(flat_dataset)

                logger.info("Opening flattened file with xarray.")
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
        logger.info("Concatenating flattened files...")
        # combined_ds = xr.open_mfdataset(intermediate_flat_filepaths,
        #                                 decode_times=False,
        #                                 decode_coords=False,
        #                                 data_vars='minimal',
        #                                 coords='minimal',
        #                                 compat='override')

        if concat_kwargs is None:
            concat_kwargs = {}

        if concat_method == "xarray-concat":
            combined_ds = xr.concat(
                xrdataset_list,
                dim=GROUP_DELIM + concat_dim,
                data_vars="minimal",
                coords="minimal",
                **concat_kwargs,
            )
        elif concat_method == "xarray-combine":
            combined_ds = xr.combine_by_coords(
                xrdataset_list,
                data_vars="minimal",
                coords="minimal",
                **concat_kwargs,
            )
        else:
            raise ValueError("Unexpected concatenation method, <%s>." % concat_method)

        benchmark_log["concatenating"] = time.time() - start_time

        if write_tmp_flat_concatenated:
            logger.info("Writing concatenated flattened temporary file to disk...")
            # Concatenated, yet still flat, file is written to disk for debugging.
            tmp_flat_concatenated_path = add_label_to_path(output_file, label="_flat_intermediate")
            combined_ds.to_netcdf(tmp_flat_concatenated_path, format="NETCDF4")
        else:
            tmp_flat_concatenated_path = None

        # The group hierarchy of the concatenated file is reconstructed (using XARRAY).
        start_time = time.time()
        logger.info("Reconstructing groups within concatenated file...")
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

    except Exception as err:
        logger.info("Stitchee encountered an error!")
        logger.error(err)
        raise err

    return output_file


def _validate_workable_files(files_to_concat, logger) -> tuple[list[str], int]:
    """Remove files from a list that are not open-able as netCDF or that are empty."""
    workable_files = []
    for file in files_to_concat:
        try:
            with open_netcdf_dataset_or_hdf_file(file, mode="r") as (dataset, file_kind):
                # with nc.Dataset(file, "r") as dataset:
                is_empty = _is_file_empty(dataset, file_kind)
                if is_empty is False:
                    workable_files.append(file)
        except OSError:
            logger.debug("Error opening <%s> as a netCDF dataset. Skipping.", file)

    number_of_workable_files = len(workable_files)

    return workable_files, number_of_workable_files


def _is_file_empty(parent_group: nc.Dataset | nc.Group | h5py.File, file_kind: str) -> bool:
    """
    Function to test if a all variable size in a dataset is 0
    """
    if file_kind == "hdf":

        def _is_hdf_group_and_subgroups_empty(data_new, group):
            is_empty = True
            for key, item in data_new[group].items():
                group_path = f"{group}{key}"
                if isinstance(item, h5py.Dataset):
                    if item.size != 0:
                        is_empty = False
                elif isinstance(item, h5py.Group):
                    is_empty = _is_hdf_group_and_subgroups_empty(
                        data_new, data_new[group_path].name + "/"
                    )

                if is_empty is False:
                    return False

        if _is_hdf_group_and_subgroups_empty(parent_group, parent_group.name) is False:
            return False

    else:
        for var in parent_group.variables.values():
            if var.size != 0:
                return False
        for child_group in parent_group.groups.values():
            return _is_file_empty(child_group, file_kind)
    return True
