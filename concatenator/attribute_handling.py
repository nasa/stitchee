"""Functions for converting "coordinates" in netCDF variable attributes
between paths that reference a group hierarchy and flattened paths.
"""

import json
from datetime import datetime, timezone

import importlib_metadata
import netCDF4

# Values needed for history_json attribute
HISTORY_JSON_SCHEMA = "https://harmony.earthdata.nasa.gov/schemas/history/0.1.0/history-v0.1.0.json"
PROGRAM = "stitchee"
PROGRAM_REF = "https://cmr.earthdata.nasa.gov:443/search/concepts/S2940253910-LARC_CLOUD"
VERSION = importlib_metadata.distribution("stitchee").version


def retrieve_history(dataset: netCDF4.Dataset) -> dict:
    """
    Retrieve history_json field from NetCDF dataset, if it exists

    Parameters
    ----------
    dataset: NetCDF Dataset representing a single granule

    Returns
    -------
    A history_json field
    """
    if "history_json" not in dataset.ncattrs():
        return {}
    history_json = dataset.getncattr("history_json")
    return json.loads(history_json)


def construct_history(input_files: list, granule_urls: list) -> dict:
    """
    Construct history JSON entry for this concatenation operation
    https://wiki.earthdata.nasa.gov/display/TRT/In-File+Provenance+Metadata+-+TRT-42

    Parameters
    ----------
    input_files: List of input files

    Returns
    -------
    History JSON constructed for this concat operation
    """
    history_json = {
        "$schema": HISTORY_JSON_SCHEMA,
        "date_time": datetime.now(tz=timezone.utc).isoformat(),
        "program": PROGRAM,
        "version": VERSION,
        "parameters": f"input_files={input_files}",
        "derived_from": granule_urls,
        "program_ref": PROGRAM_REF,
    }
    return history_json
