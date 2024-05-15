import json

import xarray as xr

from concatenator.attribute_handling import construct_history
from concatenator.stitchee import stitchee
from tests.conftest import prep_input_files


def test_construct_and_append_history_for_sample_concatenation(
    temp_toy_data_dir,
    temp_output_dir,
    ds_3dims_3vars_4coords_1group_part1,
    ds_3dims_3vars_4coords_1group_part2,
):
    output_path = str(temp_output_dir.joinpath("simple_sample_concatenated.nc"))  # type: ignore
    prepared_input_files = prep_input_files(temp_toy_data_dir, temp_output_dir)

    history_json = construct_history(prepared_input_files, prepared_input_files)

    new_history_json = json.dumps(history_json, default=str)

    output_path = stitchee(
        files_to_concat=prepared_input_files,
        output_file=output_path,
        write_tmp_flat_concatenated=True,
        keep_tmp_files=True,
        concat_method="xarray-concat",
        history_to_append=new_history_json,
        concat_dim="step",
    )
    stitcheed_dataset = xr.open_dataset(output_path)

    # Assert that the history was created by this service
    assert "stitchee" in stitcheed_dataset.attrs["history_json"]

    # Assert that the history created by this service is the only
    # line present in the history.
    assert "\n" not in stitcheed_dataset.attrs["history_json"]
