"""Concatenation service that appends data along an existing dimension, using NCO operators."""
from logging import getLogger

import netCDF4 as nc
from nco import Nco  # type: ignore

from concatenator.stitchee import _validate_workable_files

default_logger = getLogger(__name__)


def concat_netcdf_files(
    original_input_files,
    output_file,
    dim_for_record_dim="mirror_step",
    decompress_datasets=False,
    logger=default_logger,
):
    """
    Main entrypoint to merge implementation. Merges n >= 2 granules together as a single
    granule. Named in reference to original Java implementation.

    Parameters
    ----------
    input_files: list
        list of string paths to NetCDF4 files to merge
    output_file: str
        output path for merged product
    dim_for_record_dim : str
        Name of the dimension to be used as the *record* dimension for concatenation
    logger: logger
        logger object
    """
    nco = Nco()
    logger.info("Preprocessing data...")

    # Proceed to concatenate only files that are workable (can be opened and are not empty).
    input_files, _ = _validate_workable_files(original_input_files, logger)

    for i, file in enumerate(input_files):
        print(f"Checking for record dimension in file {i} ({file})..")

        # Check whether the dataset already contains a record (AKA unlimited) dimension.
        dim_names = nc.Dataset(file).dimensions
        contains_record_dim = False
        for name in dim_names:
            if nc.Dataset(file).dimensions[name].isunlimited():
                contains_record_dim = True
                print(f"  Existing record dimension identified ---> <{name}>.")

        # Convert an existing dimension to be a record dimension if one did not already exist.
        if not contains_record_dim:
            print(
                f"  No record dimension exists; making <{dim_for_record_dim}> into a record dimension.."
            )
            nco.ncks(input=file, output=file, options=["-O", f"--mk_rec_dmn {dim_for_record_dim}"])

        if decompress_datasets:
            nco.ncks(input=file, output=file, options=["-L 0"])

    # -- concatenate datasets --
    logger.info("Concatenating datasets...")
    nco.ncrcat(input=input_files, output=output_file, options=["--no_tmp_fl"])

    logger.info("Done.")
