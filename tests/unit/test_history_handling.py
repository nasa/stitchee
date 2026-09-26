"""Regression coverage for object- and array-valued processing history."""

import json
import subprocess
import sys
from datetime import UTC, datetime
from unittest.mock import patch

import netCDF4 as nc
import numpy as np
import pystac
import pytest
from harmony_service_lib.message import Message, Source

from stitchee.harmony.service_adapter import StitcheeAdapter
from stitchee.history_handling import collect_history, retrieve_history

RECORD = {
    "program": "upstream",
    "version": "1.2.3",
    "date_time": "2026-01-01T00:00:00Z",
    "parameters": [{"name": "temperature", "units": "°C"}],
    "derived_from": ["source.nc4"],
}


def write_granule(path, history, start=0):
    """Create a small numeric NetCDF granule without external fixtures."""
    with nc.Dataset(path, "w") as dataset:
        dataset.createDimension("mirror_step", 2)
        dataset.createVariable("mirror_step", "i4", ("mirror_step",))[:] = [start, start + 1]
        dataset.createVariable("science", "f4", ("mirror_step",))[:] = [start + 10, start + 11]
        group = dataset.createGroup("geolocation")
        group.createVariable("time", "f8", ("mirror_step",))[:] = [start, start + 1]
        dataset.title = "Unchanged input metadata"
        if history is not None:
            dataset.history_json = json.dumps(history)
    return path


@pytest.mark.parametrize(
    "history,expected", [(RECORD, [RECORD]), ([RECORD], [RECORD]), ([], []), (None, [])]
)
def test_retrieve_history_returns_records(tmp_path, history, expected):
    path = write_granule(tmp_path / "granule.nc4", history)
    before = path.read_bytes()
    with nc.Dataset(path) as dataset:
        result = retrieve_history(dataset)
    assert result == expected
    assert isinstance(result, list)
    assert path.read_bytes() == before


def test_invalid_history_still_raises_at_reader(tmp_path):
    path = write_granule(tmp_path / "invalid.nc4", None)
    with nc.Dataset(path, "a") as dataset:
        dataset.history_json = "not json"
    with nc.Dataset(path) as dataset, pytest.raises(json.JSONDecodeError):
        retrieve_history(dataset)


def test_collect_history_preserves_records_and_order(tmp_path):
    second = {"program": "second", "parameters": {"value": 0}}
    third = {"program": "third", "derived_from": "original.nc4"}
    histories = [RECORD, [second, third], [], None]
    paths = [
        write_granule(tmp_path / f"input{i}.nc4", history, i * 2)
        for i, history in enumerate(histories)
    ]
    snapshots = [path.read_bytes() for path in paths]
    result = json.loads(collect_history([str(path) for path in paths]))
    assert result[:-1] == [RECORD, second, third]
    assert result[-1]["program"] == "stitchee"
    assert result[-1]["derived_from"] == [str(path) for path in paths]
    assert all(isinstance(record, dict) for record in result)
    assert [path.read_bytes() for path in paths] == snapshots


def assert_output(path, inputs, second):
    with nc.Dataset(path) as dataset:
        history = json.loads(dataset.history_json)
        assert history[:-1] == [RECORD, second]
        assert history[-1]["program"] == "stitchee"
        np.testing.assert_array_equal(dataset["science"][:], [10, 11, 12, 13])
        np.testing.assert_array_equal(dataset["geolocation/time"][:], [0, 1, 2, 3])
        assert dataset.title == "Unchanged input metadata"
    for input_path, expected_bytes in inputs:
        assert input_path.read_bytes() == expected_bytes


def test_cli_preserves_single_record_history_in_real_output(tmp_path):
    second = {"program": "second", "version": "2.0"}
    first_path = write_granule(tmp_path / "first.nc4", RECORD)
    second_path = write_granule(tmp_path / "second.nc4", [second], 2)
    snapshots = [(path, path.read_bytes()) for path in [first_path, second_path]]
    output = tmp_path / "merged.nc4"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "stitchee.cli",
            str(first_path),
            str(second_path),
            "-o",
            str(output),
            "--concat_dim",
            "mirror_step",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert_output(output, snapshots, second)


def test_adapter_preserves_single_record_history_in_staged_output(tmp_path):
    second = {"program": "second", "parameters": {"value": False}}
    paths = [
        write_granule(tmp_path / "first.nc4", RECORD),
        write_granule(tmp_path / "second.nc4", [second], 2),
    ]
    snapshots = [(path, path.read_bytes()) for path in paths]
    catalog = pystac.Catalog("input", "Synthetic granules")
    for index, path in enumerate(paths):
        item = pystac.Item(
            str(index), None, [0, 0, 1, 1], datetime(2026, 1, index + 1, tzinfo=UTC), {}
        )
        item.add_asset(
            "data", pystac.Asset(path.as_uri(), media_type="application/x-netcdf4", roles=["data"])
        )
        catalog.add_item(item)
    output_dir = tmp_path / "staged"
    output_dir.mkdir()
    message = Message({"accessToken": "unused", "stagingLocation": output_dir.as_uri()})
    adapter = StitcheeAdapter(message, catalog=catalog)
    with (
        patch("stitchee.harmony.service_adapter.multi_core_download", return_value=paths),
        patch.object(adapter, "_get_item_source", return_value=Source({"collection": "C_TEST"})),
    ):
        _, result = adapter.invoke()
    items = list(result.get_items())
    assert len(items) == 1
    asset = items[0].assets["data"]
    assert asset.media_type == "application/x-netcdf4"
    assert_output(output_dir / asset.title, snapshots, second)
