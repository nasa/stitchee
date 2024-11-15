import json
import sys
from os import environ
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import pytest
from netCDF4 import Dataset

import concatenator.harmony.cli
from tests.conftest import prep_input_files


@pytest.mark.usefixtures("pass_options")
class TestBatching:
    __test_path = Path(__file__).parents[1].resolve()
    __data_path = __test_path.joinpath("data")
    __harmony_path = __data_path.joinpath("harmony")
    __granule_copies_path = __harmony_path.joinpath("granule_copies_dir")
    __granules_path = __harmony_path.joinpath("granules")

    def test_service_invoke(self, temp_output_dir):
        in_message_path = self.__harmony_path.joinpath("message.json")
        in_message_data = in_message_path.read_text()

        # test with both paged catalogs and un-paged catalogs
        for in_catalog_name in ["catalog.json", "catalog0.json"]:
            # Copy granule files, because Dataset's variable names are modified during flattening.
            # If stitchee is run two times on the same file, it will likely fail the second time.
            _ = prep_input_files(self.__granules_path, self.__granule_copies_path)

            in_catalog_path = self.__harmony_path.joinpath("source", in_catalog_name)

            test_args = [
                concatenator.harmony.cli.__file__,
                "--harmony-action",
                "invoke",
                "--harmony-input",
                in_message_data,
                "--harmony-source",
                str(in_catalog_path),
                "--harmony-metadata-dir",
                str(temp_output_dir),
                "--harmony-data-location",
                temp_output_dir.as_uri(),
            ]

            test_env = {
                "ENV": "dev",
                "OAUTH_CLIENT_ID": "",
                "OAUTH_UID": "",
                "OAUTH_PASSWORD": "",
                "OAUTH_REDIRECT_URI": "",
                "STAGING_PATH": "",
                "STAGING_BUCKET": "",
            }

            with patch.object(sys, "argv", test_args), patch.dict(environ, test_env):
                concatenator.harmony.cli.main()

            # Open the outputs
            out_catalog_path = temp_output_dir.joinpath("catalog.json")
            out_catalog = json.loads(out_catalog_path.read_text())

            item_meta = next(item for item in out_catalog["links"] if item["rel"] == "item")
            item_href = item_meta["href"]
            item_path = temp_output_dir.joinpath(item_href).resolve()

            # -- Item Verification --
            item = json.loads(item_path.read_text())
            properties = item["properties"]

            # Accumulation method checks
            assert item["bbox"] == [-4, -3, 1, 3]
            assert properties["start_datetime"] == "2020-01-02T00:00:00+00:00"
            assert properties["end_datetime"] == "2020-01-05T23:59:59+00:00"

            # -- Asset Verification --
            data = item["assets"]["data"]

            # Sanity checks on metadata
            assert data["href"].endswith("_stitched.nc4")
            assert data["title"].endswith("_stitched.nc4")
            assert data["type"] == "application/x-netcdf4"
            assert data["roles"] == ["data"]

            path = urlsplit(data["href"]).path
            dataset = Dataset(path)
            assert len(dataset["mirror_step"]) == 395
