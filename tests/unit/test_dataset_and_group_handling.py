"""Tests for manipulating netCDF groups."""

# pylint: disable=C0116, C0301

import netCDF4 as nc

from concatenator.attribute_handling import (
    _flatten_coordinate_attribute,
    regroup_coordinate_attribute,
)
from concatenator.dataset_and_group_handling import (
    _is_file_empty,
    validate_workable_files
)

from .. import data_for_tests_dir


def test_dataset_with_single_empty_input_file():
    """Ensure that a dataset with a single empty input file is propagating empty granule to the output"""
    files = [
        data_for_tests_dir
        / "unit-test-data"
        / "TEMPO_NO2_L2_V03_20240328T154353Z_S008G01.nc4"
    ]
    workable_files, number_of_workable_files = validate_workable_files(files, None)
    assert number_of_workable_files == 1


def test_dataset_with_singleton_null_values_is_identified_as_empty():
    """Ensure that a dataset with only null arrays with 1-length dimensions is identified as empty."""
    singleton_null_values_file = (
        data_for_tests_dir
        / "unit-test-data"
        / "singleton_null_variables-TEMPO_NO2_L2_V01_20240123T231358Z_S013G03_product_vertical_column_total.nc4"
    )
    with nc.Dataset(singleton_null_values_file) as ds:
        assert _is_file_empty(ds)


def test_toy_dataset_with_singleton_null_values_is_identified_as_empty(toy_empty_dataset):
    """Ensure that a dataset with only null arrays with 1-length dimensions is identified as empty."""
    with nc.Dataset(toy_empty_dataset) as ds:
        assert _is_file_empty(ds)


def test_dataset_with_values_is_identified_as_not_empty(ds_3dims_3vars_4coords_1group_part1):
    """Ensure that a dataset with non-null arrays is identified as NOT empty."""
    with nc.Dataset(ds_3dims_3vars_4coords_1group_part1) as ds:
        assert _is_file_empty(ds) is False


def test_coordinate_attribute_flattening():
    # Case with groups present and double spaces.
    assert (
        _flatten_coordinate_attribute(
            "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
        )
        == "__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude"
    )

    # Case with NO groups present and single spaces.
    assert (
        _flatten_coordinate_attribute(
            "time longitude latitude ozone_profile_pressure ozone_profile_altitude"
        )
        == "__time __longitude __latitude __ozone_profile_pressure __ozone_profile_altitude"
    )


def test_coordinate_attribute_regrouping():
    # Case with groups present and double spaces.
    assert (
        regroup_coordinate_attribute(
            "__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude"
        )
        == "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
    )

    # Case with NO groups present and single spaces.
    assert (
        regroup_coordinate_attribute(
            "__time __longitude __latitude __ozone_profile_pressure __ozone_profile_altitude"
        )
        == "time longitude latitude ozone_profile_pressure ozone_profile_altitude"
    )
