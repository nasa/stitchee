from logging import getLogger

import netCDF4 as nc
from nco import Nco

default_logger = getLogger(__name__)


def _is_file_empty(parent_group):
    """
    Function to test if a all variable size in a dataset is 0
    """

    for var in parent_group.variables.values():
        if var.size != 0:
            return False
    for child_group in parent_group.groups.values():
        return _is_file_empty(child_group)
    return True


def concat_netcdf_files(original_input_files,
                        output_file,
                        dim_for_record_dim='mirror_step',
                        logger=default_logger):
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

    # -- initial preprocessing --
    logger.info('Preprocessing data...')
    input_files = []

    # only concatenate files that are not empty
    for file in original_input_files:
        with nc.Dataset(file, 'r') as dataset:
            is_empty = _is_file_empty(dataset)
            if is_empty is False:
                input_files.append(file)

    logger.info(f'Creating new record dimension from dim={dim_for_record_dim}')
    for i, file in enumerate(input_files):
        print(f"{i} | ncks on file: {file}")
        nco.ncks(input=file, output=file,
                 options=["-O", f"--mk_rec_dmn {dim_for_record_dim}"])

    # -- concatenate datasets --
    logger.info('Concatenating datasets...')
    nco.ncrcat(input=input_files, output=output_file)

    logger.info('Done.')
