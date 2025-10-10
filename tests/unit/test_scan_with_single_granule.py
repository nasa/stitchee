"""Test for processing single granule scan."""

import os

import xarray as xr

from stitchee.concatenate import concatenate

from .. import data_for_tests_dir


def test_no_files_to_concatenate(temp_output_dir):
    input_granule = str(
        data_for_tests_dir
        / "harmony"
        / "granules"
        / "TEMPO_NO2_L2_V03_20240601T210934Z_S012G01_subsetted.nc4"
    )
    output_path = concatenate(
        [input_granule],
        output_file=os.path.join(temp_output_dir, "output.nc"),
        concat_dim="mirror_step",
    )

    assert xr.open_datatree(input_granule).identical(xr.open_datatree(output_path))
