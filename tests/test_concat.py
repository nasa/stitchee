"""Tests for concatenation logic."""

# pylint: disable=C0116

from pathlib import Path

import netCDF4 as nc
import pytest

from concatenator.stitchee import stitchee

from . import data_for_tests_dir
from .conftest import prep_input_files


@pytest.mark.usefixtures("pass_options")
class TestConcat:
    """Main concatenation testing class."""

    def run_verification_with_stitchee(
        self,
        input_dir: Path,
        output_dir: Path,
        output_name: str,
        concat_method: str = "xarray-concat",
        record_dim_name: str = "mirror_step",
        concat_kwargs: dict | None = None,
    ):
        output_path = str(output_dir.joinpath(output_name))  # type: ignore
        prepared_input_files = prep_input_files(input_dir, output_dir)

        if concat_kwargs is None:
            concat_kwargs = {}

        output_path = stitchee(
            files_to_concat=prepared_input_files,
            output_file=output_path,
            write_tmp_flat_concatenated=True,
            keep_tmp_files=True,
            concat_method=concat_method,
            concat_dim=record_dim_name,
            concat_kwargs=concat_kwargs,
        )

        merged_dataset = nc.Dataset(output_path)

        # Verify that the length of the record dimension in the concatenated file equals
        #   the sum of the lengths across the input files
        length_sum = 0
        for file in prepared_input_files:
            length_sum += len(nc.Dataset(file).variables[record_dim_name])
        assert length_sum == len(merged_dataset.variables[record_dim_name])

        return merged_dataset

    def test_simple_sample(
        self,
        temp_toy_data_dir,
        temp_output_dir,
        ds_3dims_3vars_4coords_1group_part1,
        ds_3dims_3vars_4coords_1group_part2,
        ds_3dims_3vars_4coords_1group_part3,
    ):
        record_dim_name = "step"

        merged_data = self.run_verification_with_stitchee(
            input_dir=temp_toy_data_dir,
            output_dir=temp_output_dir,
            output_name="simple_sample_concatenated.nc",
            record_dim_name=record_dim_name,
            concat_method="xarray-concat",
        )

        # Check that the concatenated dimension elements in the result are sorted.
        assert all(
            a == b
            for a, b in zip(
                merged_data.variables[record_dim_name][:],
                sorted(merged_data.variables[record_dim_name][:]),
            )
        )

    def test_tempo_no2_concat_with_stitchee(self, temp_output_dir):
        self.run_verification_with_stitchee(
            input_dir=data_for_tests_dir / "tempo/no2",
            output_dir=temp_output_dir,
            output_name="tempo_no2_stitcheed.nc",
            concat_method="xarray-concat",
        )

    def test_tempo_no2_subsetter_output_concat_with_stitchee(self, temp_output_dir):
        self.run_verification_with_stitchee(
            input_dir=data_for_tests_dir / "tempo/no2_subsetted",
            output_dir=temp_output_dir,
            output_name="tempo_no2_stitcheed.nc",
            concat_method="xarray-concat",
        )

    def test_tempo_hcho_concat_with_stitchee(self, temp_output_dir):
        self.run_verification_with_stitchee(
            input_dir=data_for_tests_dir / "tempo/hcho",
            output_dir=temp_output_dir,
            output_name="tempo_hcho_stitcheed.nc",
            concat_method="xarray-concat",
        )

    def test_tempo_cld04_concat_with_stitchee(self, temp_output_dir):
        self.run_verification_with_stitchee(
            input_dir=data_for_tests_dir / "tempo/cld04",
            output_dir=temp_output_dir,
            output_name="tempo_cld04_stitcheed.nc",
            concat_method="xarray-concat",
        )

    # def test_tempo_o3prof_concat_with_stitchee(self):
    #     self.run_verification_with_stitchee(
    #         "tempo/o3prof", "tempo_o3prof_bee_concatenated.nc", concat_method="xarray-concat"
    #     )

    # def test_icesat_concat_with_stitchee(self):
    #     self.run_verification_with_stitchee('icesat', 'icesat_concat_with_stitchee.nc')
    #
    def test_ceres_concat_with_stitchee(self, temp_output_dir):
        self.run_verification_with_stitchee(
            input_dir=data_for_tests_dir / "ceres-subsetter-output",
            output_dir=temp_output_dir,
            output_name="ceres_bee_concatenated.nc",
            concat_method="xarray-combine",
            record_dim_name="time",
            concat_kwargs={"compat": "override", "combine_attrs": "override"},
        )

    def test_ceres_flash_concat_with_stitchee(self, temp_output_dir):
        self.run_verification_with_stitchee(
            input_dir=data_for_tests_dir / "ceres_flash-subsetter-output",
            output_dir=temp_output_dir,
            output_name="ceres_flash_bee_concatenated.nc",
            concat_method="xarray-combine",
            record_dim_name="time",
            concat_kwargs={"compat": "override", "combine_attrs": "override"},
        )

    # def test_ceres_flash_concat_with_stitchee(self):
    #     self.run_verification_with_stitchee('ceres_flash-subsetter-output',
    #                                          'ceres_flash_concat_with_stitchee.nc',
    #                                          record_dim_name='time')
