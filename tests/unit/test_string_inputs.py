"""String-bearing NetCDF files must not be discarded as unreadable or empty."""

from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

from stitchee.concatenate import concatenate
from stitchee.file_ops import _is_file_empty, validate_workable_files


def write_input(path: Path, kind: str, nested: bool, offset: int = 0) -> None:
    """Write strings before numeric measurements, using real NetCDF variables."""
    with nc.Dataset(path, "w") as dataset:
        group = dataset.createGroup("measurements") if nested else dataset
        group.createDimension("obs", 2)
        labels = [f"A{offset}", f"B{offset}"]
        if kind == "vlen":
            variable = group.createVariable("station", str, ("obs",))
            variable[:] = np.array(labels, dtype=object)
        else:
            group.createDimension("strlen", 2)
            variable = group.createVariable("station", "S1", ("obs", "strlen"))
            variable[:] = np.array([list(label) for label in labels], dtype="S1")
            if kind == "decoded_char":
                variable.setncattr("_Encoding", "utf-8")
        group.createVariable("time", "i4", ("obs",))[:] = [offset, offset + 1]
        group.createVariable("value", "f4", ("obs",))[:] = [10 + offset, 20 + offset]


@pytest.mark.parametrize("kind", ["vlen", "char", "decoded_char"])
@pytest.mark.parametrize("nested", [False, True])
def test_populated_strings_preserve_valid_files(tmp_path, kind, nested):
    """A text variable must not hide subsequent numeric data or child groups."""
    path = tmp_path / "input.nc"
    write_input(path, kind, nested)
    with nc.Dataset(path) as dataset:
        assert _is_file_empty(dataset) is False
    assert validate_workable_files([str(path)]) == ([str(path)], 1)


@pytest.mark.parametrize("kind", ["vlen", "char"])
@pytest.mark.parametrize("populated", [False, True])
def test_string_fill_values_remain_empty(tmp_path, kind, populated):
    """Respect fill values and masks without applying isnan to text."""
    path = tmp_path / "fill.nc"
    with nc.Dataset(path, "w") as dataset:
        dataset.createDimension("obs", 2)
        dtype = str if kind == "vlen" else "S1"
        fill = "missing" if kind == "vlen" else b"?"
        variable = dataset.createVariable("text", dtype, ("obs",), fill_value=fill)
        variable[:] = np.array(
            [fill, "A" if populated else fill], dtype=object if kind == "vlen" else "S1"
        )
    with nc.Dataset(path) as dataset:
        assert _is_file_empty(dataset) is (not populated)


@pytest.mark.parametrize("kind", ["vlen", "char"])
def test_zero_length_strings_are_empty(tmp_path, kind):
    """Zero-size variables remain empty without inspecting their element type."""
    path = tmp_path / "empty.nc"
    with nc.Dataset(path, "w") as dataset:
        dataset.createDimension("obs", None)
        dataset.createVariable("text", str if kind == "vlen" else "S1", ("obs",))
    with nc.Dataset(path) as dataset:
        assert _is_file_empty(dataset) is True


def test_scalar_string_is_valid_data(tmp_path):
    """NetCDF can return a Python string for a zero-dimensional string variable."""
    path = tmp_path / "scalar.nc"
    with nc.Dataset(path, "w") as dataset:
        variable = dataset.createVariable("station", str)
        variable[...] = "station-A"
    with nc.Dataset(path) as dataset:
        assert _is_file_empty(dataset) is False


@pytest.mark.parametrize("kind", ["vlen", "char", "decoded_char"])
@pytest.mark.parametrize("nested", [False, True])
def test_concatenation_keeps_string_bearing_inputs(tmp_path, kind, nested):
    """Verify the complete public file-to-file path and its numeric output."""
    inputs = [tmp_path / "first.nc", tmp_path / "second.nc"]
    for offset, path in zip([0, 2], inputs, strict=True):
        write_input(path, kind, nested, offset)
    before = [path.read_bytes() for path in inputs]
    output = tmp_path / "stitched.nc"
    # An empty root in the nested fixture has no concatenation dimension.
    kwargs = {"data_vars": "all"} if nested else None
    assert concatenate(
        [str(path) for path in inputs], str(output), concat_dim="obs", concat_kwargs=kwargs
    ) == str(output.resolve())
    with nc.Dataset(output) as dataset:
        group = dataset.groups["measurements"] if nested else dataset
        np.testing.assert_array_equal(group["time"][:], [0, 1, 2, 3])
        np.testing.assert_array_equal(group["value"][:], [10, 20, 12, 22])
        labels = group["station"][:]
        if kind == "char":
            labels = nc.chartostring(labels)
        np.testing.assert_array_equal(labels, ["A0", "B0", "A2", "B2"])
    assert [path.read_bytes() for path in inputs] == before
