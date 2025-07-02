"""Tests for file operations."""

import logging
from pathlib import Path

# pylint: disable=C0116, C0301
import netCDF4 as nc
import pytest

from concatenator.file_ops import (
    _is_file_empty,
    validate_input_path,
    validate_output_path,
    validate_workable_files,
)

from .. import data_for_tests_dir
from ..conftest import path_str

module_logger = logging.getLogger(__name__)


def test_validate_bad_output_paths():
    path_to_file_that_exists = str(
        data_for_tests_dir / "unit-test-data" / "TEMPO_NO2_L2_V03_20240328T154353Z_S008G01.nc4"
    )

    with pytest.raises(FileExistsError):
        validate_output_path(path_to_file_that_exists, overwrite=False)

    with pytest.raises(TypeError):
        validate_output_path(str(data_for_tests_dir), overwrite=False)


def test_validate_bad_non_existent_input_path():
    path_to_file_that_does_not_exist = str(
        data_for_tests_dir / "unit-test-data" / "non-existent.nc4"
    )

    with pytest.raises(TypeError):
        validate_input_path([path_to_file_that_does_not_exist])

    with pytest.raises(TypeError):
        validate_input_path([])


def test_dataset_with_single_empty_input_file():
    """Ensure that a dataset with a single empty input file is propagating empty granule to the output"""
    files_to_concat = [
        data_for_tests_dir / "unit-test-data" / "TEMPO_NO2_L2_V03_20240328T154353Z_S008G01.nc4"
    ]
    workable_files, number_of_workable_files = validate_workable_files(files_to_concat)
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
    toy_null_dataset,
):
    """Ensure that a dataset with only null arrays with 1-length dimensions is identified as empty."""
    with nc.Dataset(toy_null_dataset) as ds:
        assert _is_file_empty(ds)


def test_dataset_with_values_is_identified_as_not_empty(
    ds_3dims_3vars_3coords_1group_part1,
):
    """Ensure that a dataset with non-null arrays is identified as NOT empty."""
    with nc.Dataset(ds_3dims_3vars_3coords_1group_part1) as ds:
        assert _is_file_empty(ds) is False


@pytest.mark.usefixtures("pass_options")
class TestFileHandling:
    __test_path = Path(__file__).parents[1].resolve()
    __data_path = __test_path.joinpath("data")
    __harmony_path = __data_path.joinpath("harmony")
    __granules_path = __harmony_path.joinpath("granules")

    def test_workable_files_validation(self, temp_output_dir):
        filepaths = [
            path_str(
                self.__granules_path,
                "TEMPO_NO2_L2_V03_20240601T210934Z_S012G01_subsetted.nc4",
            ),
            path_str(
                self.__granules_path,
                "TEMPO_NO2_L2_V03_20240601T211614Z_S012G02_subsetted.nc4",
            ),
            path_str(
                self.__granules_path,
                "TEMPO_NO2_L2_V03_20240601T212254Z_S012G03_subsetted.nc4",
            ),
        ]

        assert validate_workable_files(filepaths, module_logger)[1] == 3
