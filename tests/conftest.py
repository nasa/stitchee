"""Initial configuration for tests."""

import typing
from pathlib import Path

import netCDF4 as nc
import pytest


class DataDirs(typing.NamedTuple):
    test_path: Path
    test_data_path: Path


class TempDirs(typing.NamedTuple):
    output_path: Path
    toy_data_path: Path


def pytest_addoption(parser):
    """Sets up optional argument to keep temporary testing directory."""
    parser.addoption(
        "--keep-tmp",
        action="store_true",
        help="Keep temporary directory after testing. Useful for debugging.",
    )


@pytest.fixture(scope="class")
def pass_options(request):
    """Adds optional argument to a test class."""
    request.cls.KEEP_TMP = request.config.getoption("--keep-tmp")


@pytest.fixture(scope="session")
def temp_toy_data_dir(tmpdir_factory) -> Path:
    return Path(tmpdir_factory.mktemp("toy-"))


@pytest.fixture(scope="function", autouse=True)
def temp_output_dir(tmpdir_factory) -> Path:
    return Path(tmpdir_factory.mktemp("tmp-"))


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


@pytest.fixture(scope="session")
def ds_3dims_3vars_4coords_1group_part1(temp_toy_data_dir) -> Path:
    filepath = temp_toy_data_dir / "test_3dims_3vars_4coords_1group_part1.nc"

    f = nc.Dataset(filename=filepath, mode="w")
    f = add_to_ds_3dims_3vars_4coords_1group_with_step_values(f, step_values=[9, 10, 11])
    f.close()

    return filepath


@pytest.fixture(scope="session")
def ds_3dims_3vars_4coords_1group_part2(temp_toy_data_dir):
    filepath = temp_toy_data_dir / "test_3dims_3vars_4coords_1group_part2.nc"

    f = nc.Dataset(filename=filepath, mode="w")
    f = add_to_ds_3dims_3vars_4coords_1group_with_step_values(f, step_values=[12, 13, 14])
    f.close()

    return filepath
