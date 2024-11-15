"""Tests for manipulating netCDF groups."""

# pylint: disable=C0116, C0301
import logging
from pathlib import Path

import pytest

from concatenator.dataset_and_group_handling import validate_workable_files

from ..conftest import path_str

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("pass_options")
class TestGroupHandling:
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

        assert validate_workable_files(filepaths, logger)[1] == 3
