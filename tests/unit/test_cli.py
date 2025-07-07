import sys
from unittest.mock import patch

import pytest

import stitchee
from stitchee.cli import parse_args

from ..conftest import granules_path, path_str


def test_parser():
    parsed = parse_args(
        [
            "ncfile1",
            "ncfile2",
            "ncfile3",
            "-o",
            "outfile",
            "--concat_dim",
            "mirror_step",
        ]
    )

    assert parsed.input == ["ncfile1", "ncfile2", "ncfile3"]
    assert parsed.output_path == "outfile"
    assert parsed.concat_dim == "mirror_step"
    assert parsed.concat_method == "xarray-concat"
    assert parsed.verbose is False


@pytest.mark.usefixtures("pass_options")
class TestBatching:
    def test_cli_with_three_filepaths(self, temp_output_dir):
        test_args = [
            stitchee.cli.__file__,
            path_str(granules_path, "TEMPO_NO2_L2_V03_20240601T210934Z_S012G01_subsetted.nc4"),
            path_str(granules_path, "TEMPO_NO2_L2_V03_20240601T211614Z_S012G02_subsetted.nc4"),
            path_str(granules_path, "TEMPO_NO2_L2_V03_20240601T212254Z_S012G03_subsetted.nc4"),
            "--verbose",
            "-o",
            path_str(temp_output_dir, "test_cli_output.nc"),
            "--concat_method",
            "xarray-concat",
            "--concat_dim",
            "mirror_step",
        ]

        with patch.object(sys, "argv", test_args):
            stitchee.cli.main()

    def test_cli_with_one_directorypath(self, temp_output_dir):
        test_args = [
            stitchee.cli.__file__,
            str(granules_path),
            "--verbose",
            "-o",
            path_str(temp_output_dir, "test_cli_output.nc"),
            "--concat_method",
            "xarray-concat",
            "--concat_dim",
            "mirror_step",
        ]

        with patch.object(sys, "argv", test_args):
            stitchee.cli.main()

    def test_cli_with_one_netCDFpath(self, temp_output_dir):
        test_args = [
            stitchee.cli.__file__,
            path_str(granules_path, "TEMPO_NO2_L2_V03_20240601T210934Z_S012G01_subsetted.nc4"),
            "--verbose",
            "-o",
            path_str(temp_output_dir, "test_cli_output.nc"),
            "--concat_method",
            "xarray-concat",
            "--concat_dim",
            "mirror_step",
        ]

        with patch.object(sys, "argv", test_args):
            stitchee.cli.main()

    def test_cli_with_one_path_to_text_listing_of_three_files(
        self, temp_output_dir, text_file_with_three_paths
    ):
        test_args = [
            stitchee.cli.__file__,
            str(text_file_with_three_paths),
            "--verbose",
            "-o",
            path_str(temp_output_dir, "test_cli_output.nc"),
            "--concat_method",
            "xarray-concat",
            "--concat_dim",
            "mirror_step",
        ]

        with patch.object(sys, "argv", test_args):
            stitchee.cli.main()
