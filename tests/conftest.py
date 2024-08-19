"""Initial configuration for tests."""

import shutil
import typing
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

test_path = Path(__file__).parents[0].resolve()
data_path = test_path.joinpath("data")
harmony_path = data_path.joinpath("harmony")
granules_path = harmony_path.joinpath("granules")


class DataDirs(typing.NamedTuple):
    test_path: Path
    test_data_path: Path


class TempDirs(typing.NamedTuple):
    output_path: Path
    toy_data_path: Path


def path_str(dir_path: Path, filename: str) -> str:
    return str(dir_path.joinpath(filename))


def pytest_addoption(parser):
    """Sets up optional argument to keep temporary testing directory."""
    parser.addoption(
        "--keep-tmp",
        action="store_true",
        help="Keep temporary directory after testing. Useful for debugging.",
    )


def prep_input_files(input_dir: Path, output_dir: Path) -> list[str]:
    """Prepare input by copying from the original test data directory."""
    input_files = []
    for filepath in input_dir.iterdir():
        if Path(filepath).suffix.lower() in (".nc", ".nc4", ".h5", ".hdf"):
            copied_input_new_path = output_dir / Path(filepath).name  # type: ignore
            shutil.copyfile(filepath, copied_input_new_path)
            input_files.append(str(copied_input_new_path))
    return input_files


@pytest.fixture(scope="class")
def pass_options(request):
    """Adds optional argument to a test class."""
    request.cls.KEEP_TMP = request.config.getoption("--keep-tmp")


@pytest.fixture(scope="function")
def temp_toy_data_dir(tmpdir_factory) -> Path:
    return Path(tmpdir_factory.mktemp("toy-"))


@pytest.fixture(scope="function", autouse=True)
def temp_output_dir(tmpdir_factory) -> Path:
    return Path(tmpdir_factory.mktemp("tmp-"))


@pytest.fixture(scope="function")
def toy_empty_dataset(temp_toy_data_dir):
    """Creates groups, dimensions, variables; and uses chosen step values in an open dataset"""

    filepath = temp_toy_data_dir / "test_empty_dataset.nc"

    f = nc.Dataset(filename=filepath, mode="w")

    grp1 = f.createGroup("Group1")

    # Root-level Dimensions/Variables
    f.createDimension("step", 1)
    f.createDimension("track", 1)
    f.createVariable("step", "f4", ("step",), fill_value=False)
    f.createVariable("track", "f4", ("track",), fill_value=False)
    f.createVariable("var0", "f4", ("step", "track"))

    #
    f["step"][:] = [np.nan]
    f["track"][:] = [np.nan]
    f["var0"][:] = [np.nan]

    # Group 1 Dimensions/Variables
    grp1.createVariable("var1", "f8", ("step", "track"))
    #
    grp1["var1"][:] = [np.nan]

    f.close()

    return filepath


def add_to_ds_3dims_3vars_4coords_1group_with_step_values(open_ds: nc.Dataset, step_values: list):
    """Creates groups, dimensions, variables; and uses chosen step values in an open dataset"""
    grp1 = open_ds.createGroup("Group1")

    # Root-level Dimensions/Variables
    open_ds.createDimension("step", 3)
    open_ds.createDimension("track", 7)
    open_ds.createVariable("step", "i2", ("step",), fill_value=False)
    open_ds.createVariable("track", "i2", ("track",), fill_value=False)
    open_ds.createVariable("var0", "f4", ("step", "track"))
    #
    open_ds["step"][:] = step_values
    open_ds["track"][:] = [1, 2, 3, 4, 5, 6, 7]
    open_ds["var0"][:] = [
        [33, 78, 65, 12, 85, 35, 44],
        [64, 24, 87, 12, 54, 82, 24],
        [66, 18, 99, 52, 77, 88, 59],
    ]

    # Group 1 Dimensions/Variables
    grp1.createDimension("level", 2)
    grp1.createVariable("var1", "f8", ("step", "track"))
    grp1.createVariable("var2", "f4", ("step", "track", "level"))
    #
    grp1["var1"][:] = [
        [200, 300, 400, 500, 600, 700, 800],
        [200, 300, 400, 500, 600, 700, 800],
        [200, 300, 400, 500, 600, 700, 800],
    ]
    grp1["var2"][:] = [
        [[200, 150], [300, 150], [400, 150], [500, 150], [600, 150], [700, 150], [800, 150]],
        [[200, 150], [300, 150], [400, 150], [500, 150], [600, 150], [700, 150], [800, 150]],
        [[200, 150], [300, 150], [400, 150], [500, 150], [600, 150], [700, 150], [800, 150]],
    ]

    return open_ds


@pytest.fixture(scope="function")
def ds_3dims_3vars_4coords_1group_part1(temp_toy_data_dir) -> Path:
    filepath = temp_toy_data_dir / "test_3dims_3vars_4coords_1group_part1.nc"

    f = nc.Dataset(filename=filepath, mode="w")
    f = add_to_ds_3dims_3vars_4coords_1group_with_step_values(f, step_values=[9, 10, 11])
    f.close()

    return filepath


@pytest.fixture(scope="function")
def ds_3dims_3vars_4coords_1group_part2(temp_toy_data_dir):
    filepath = temp_toy_data_dir / "test_3dims_3vars_4coords_1group_part2.nc"

    f = nc.Dataset(filename=filepath, mode="w")
    f = add_to_ds_3dims_3vars_4coords_1group_with_step_values(f, step_values=[12, 13, 14])
    f.close()

    return filepath


@pytest.fixture(scope="function")
def ds_3dims_3vars_4coords_1group_part3(temp_toy_data_dir):
    filepath = temp_toy_data_dir / "test_3dims_3vars_4coords_1group_part3.nc"

    f = nc.Dataset(filename=filepath, mode="w")
    f = add_to_ds_3dims_3vars_4coords_1group_with_step_values(f, step_values=[6, 7, 8])
    f.close()

    return filepath


@pytest.fixture(scope="function")
def text_file_with_three_paths(temp_toy_data_dir) -> Path:
    filepath = temp_toy_data_dir / "text_file_with_paths.txt"

    paths = [
        path_str(granules_path, x)
        for x in [
            "TEMPO_NO2_L2_V03_20240601T210934Z_S012G01_subsetted.nc4",
            "TEMPO_NO2_L2_V03_20240601T211614Z_S012G02_subsetted.nc4",
            "TEMPO_NO2_L2_V03_20240601T212254Z_S012G03_subsetted.nc4",
        ]
    ]

    contents = f"""{paths[0]}
{paths[1]}
{paths[2]}
"""
    with open(filepath, "w") as f:
        f.write(contents)

    return filepath
