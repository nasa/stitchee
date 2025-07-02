"""Tests for concatenation errors."""

# pylint: disable=C0116

import os

import pytest

from concatenator.stitchee import stitchee


def test_no_files_to_concatenate(temp_output_dir):
    with pytest.raises(ValueError, match="files_to_concat cannot be empty"):
        stitchee([], output_file=os.path.join(temp_output_dir, "blank.nc"))


def test_invalid_concat_method(temp_output_dir, toy_null_dataset):
    with pytest.raises(ValueError, match="Unexpected concatenation method"):
        stitchee(
            [toy_null_dataset],
            output_file=os.path.join(temp_output_dir, "blank.nc"),
            concat_method="unknown-concat",
        )


def test_concat_dim_error_not_supplied_when_required(temp_output_dir, toy_null_dataset):
    with pytest.raises(
        ValueError, match="concat_dim is required when using 'xarray-concat' method"
    ):
        stitchee(
            [toy_null_dataset],
            output_file=os.path.join(temp_output_dir, "blank.nc"),
            concat_method="xarray-concat",
        )


def test_concat_dim_warning_when_supplied_but_not_used(temp_output_dir, toy_null_dataset):
    with pytest.warns(UserWarning, match="'concat_dim' was specified but will not be used"):
        stitchee(
            [toy_null_dataset],
            output_file=os.path.join(temp_output_dir, "blank.nc"),
            concat_method="xarray-combine",
            concat_dim="some_dim",
        )


def test_concat_sorting_variable_not_present_in_data(
    temp_output_dir, ds_3dims_3vars_3coords_1group_part1, ds_3dims_3vars_3coords_1group_part2
):
    with pytest.raises(KeyError):
        stitchee(
            [ds_3dims_3vars_3coords_1group_part1, ds_3dims_3vars_3coords_1group_part2],
            output_file=os.path.join(temp_output_dir, "blank.nc"),
            concat_dim="step",
            sorting_variable="unknown_variable",
        )
