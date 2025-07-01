"""Tests for concatenation logic."""

# pylint: disable=C0116

from pathlib import Path

import netCDF4 as nc
import pytest

import concatenator
from concatenator.stitchee import stitchee
from tests import data_for_tests_dir
from tests.conftest import prep_input_files


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
        sorting_variable: str | None = None,
    ):
        output_path = str(output_dir.joinpath(output_name))  # type: ignore
        prepared_input_files = prep_input_files(input_dir, output_dir)

        if concat_kwargs is None:
            concat_kwargs = {}

        output_path = stitchee(
            files_to_concat=prepared_input_files,
            output_file=output_path,
            concat_method=concat_method,
            concat_dim=record_dim_name,
            concat_kwargs=concat_kwargs,
            sorting_variable=sorting_variable,
        )

        merged_dataset = nc.Dataset(output_path)

        # Verify that the length of the record dimension in the concatenated file equals
        #   the sum of the lengths across the input files
        original_files_length_sum = 0
        for file in prepared_input_files:
            # length_sum += len(nc.Dataset(file).variables[record_dim_name])
            with nc.Dataset(file) as ncds:
                try:
                    original_files_length_sum += ncds.dimensions[record_dim_name].size
                except KeyError:
                    original_files_length_sum += ncds.dimensions[
                        concatenator.group_delim + record_dim_name
                    ].size

        try:
            merged_file_length = merged_dataset.dimensions[record_dim_name].size
        except KeyError:
            merged_file_length = merged_dataset.dimensions[
                concatenator.group_delim + record_dim_name
            ].size

        assert original_files_length_sum == merged_file_length

        return merged_dataset

    def test_simple_sample(
        self,
        temp_toy_data_dir,
        temp_output_dir,
        ds_3dims_3vars_3coords_1group_part1,
        ds_3dims_3vars_3coords_1group_part2,
        ds_3dims_3vars_3coords_1group_part3,
    ):
        record_dim_name = "step"

        merged_data = self.run_verification_with_stitchee(
            input_dir=temp_toy_data_dir,
            output_dir=temp_output_dir,
            output_name="simple_sample_concatenated.nc",
            record_dim_name=record_dim_name,
            concat_method="xarray-concat",
            sorting_variable=record_dim_name,
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

    # def test_tempo_no2_subsetter_output_concat_with_stitchee(self, temp_output_dir):
    #     self.run_verification_with_stitchee(
    #         input_dir=data_for_tests_dir / "tempo/no2_subsetted",
    #         output_dir=temp_output_dir,
    #         output_name="tempo_no2_stitcheed.nc",
    #         concat_method="xarray-concat",
    #     )

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
