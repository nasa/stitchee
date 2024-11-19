"""Tests for manipulating netCDF groups."""

# pylint: disable=C0116, C0301

import netCDF4 as nc

from concatenator.dataset_and_group_handling import (
    _get_nested_group,
    _is_file_empty,
    validate_workable_files,
)

from .. import data_for_tests_dir


def test_dataset_with_single_empty_input_file():
    """Ensure that a dataset with a single empty input file is propagating empty granule to the output"""
    files_to_concat = [
        data_for_tests_dir / "unit-test-data" / "TEMPO_NO2_L2_V03_20240328T154353Z_S008G01.nc4"
    ]
    workable_files, number_of_workable_files = validate_workable_files(files_to_concat, None)
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


def test_toy_dataset_with_singleton_null_values_is_identified_as_empty(
    toy_empty_dataset,
):
    """Ensure that a dataset with only null arrays with 1-length dimensions is identified as empty."""
    with nc.Dataset(toy_empty_dataset) as ds:
        assert _is_file_empty(ds)


def test_dataset_with_values_is_identified_as_not_empty(
    ds_3dims_3vars_3coords_1group_part1,
):
    """Ensure that a dataset with non-null arrays is identified as NOT empty."""
    with nc.Dataset(ds_3dims_3vars_3coords_1group_part1) as ds:
        assert _is_file_empty(ds) is False


def test_get_nested_group(ds_3dims_3vars_3coords_1group_part1):
    """Ensure that the retrieved group is correct."""
    with nc.Dataset(ds_3dims_3vars_3coords_1group_part1) as ds:
        group_obj = _get_nested_group(ds, "__Group1__level")
        assert isinstance(group_obj, nc.Group)


def test_get_root_group(ds_3dims_3vars_3coords_1group_part1):
    """Ensure that the retrieved group is correct."""
    with nc.Dataset(ds_3dims_3vars_3coords_1group_part1) as ds:
        group_obj = _get_nested_group(ds, "__track")
        assert group_obj == ds


def test_get_root_group_when_no_delimiter_present(ds_3dims_3vars_3coords_1group_part1):
    """Ensure that the retrieved group is correct."""
    with nc.Dataset(ds_3dims_3vars_3coords_1group_part1) as ds:
        group_obj = _get_nested_group(ds, "track")
        assert group_obj == ds
