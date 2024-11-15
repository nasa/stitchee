"""Functions for converting "coordinates" in netCDF variable attributes
between paths that reference a group hierarchy and flattened paths.
"""

import json
import re
from datetime import datetime, timezone

import importlib_metadata
import netCDF4

import concatenator

# Values needed for history_json attribute
HISTORY_JSON_SCHEMA = (
    "https://harmony.earthdata.nasa.gov/schemas/history/0.1.0/history-v0.1.0.json"
)
PROGRAM = "stitchee"
PROGRAM_REF = (
    "https://cmr.earthdata.nasa.gov:443/search/concepts/S2940253910-LARC_CLOUD"
)
VERSION = importlib_metadata.distribution("stitchee").version


def regroup_coordinate_attribute(attribute_string: str) -> str:
    """
    Examples
    --------
    >>> coord_att = "__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude"
    >>> flatten_string_with_groups(coord_att)
        Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude

    Parameters
    ----------
    attribute_string : str

    Returns
    -------
    str
    """
    # Use the separator that's in the attribute string only if all separators in the string are the same.
    # Otherwise, we will use our own default separator.
    whitespaces = re.findall(r"\s+", attribute_string)
    if len(set(whitespaces)) <= 1:
        new_sep = whitespaces[0]
    else:
        new_sep = concatenator.coord_delim

    return new_sep.join(
        "/".join(c.split(concatenator.group_delim))[1:]
        for c in attribute_string.split()  # split on any whitespace
    )


def flatten_coordinate_attribute_paths(
    dataset: netCDF4.Dataset, var: netCDF4.Variable, variable_name: str
) -> None:
    """Flatten the paths of variables referenced in the 'coordinates' attribute."""
    if "coordinates" in var.ncattrs():
        coord_att = var.getncattr("coordinates")

        new_coord_att = flatten_string_with_groups(coord_att)

        dataset.variables[variable_name].setncattr("coordinates", new_coord_att)


def flatten_string_with_groups(str_with_groups: str) -> str:
    """Determine separator and flatten string specifying group membership via "/".

    Applies to variable paths or attributes, even for the root level.

    Examples
    --------
    >>> coord_att = "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
    >>> flatten_string_with_groups(coord_att)
        __Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude

    Parameters
    ----------
    str_with_groups : str

    Returns
    -------
    str
    """
    # Use the separator that's in the attribute string only if all separators in the string are the same.
    # Otherwise, we will use our own default separator.
    whitespaces = re.findall(r"\s+", str_with_groups)
    if len(set(whitespaces)) == 0:
        new_sep = ""
    elif len(set(whitespaces)) == 1:
        new_sep = whitespaces[0]
    else:
        new_sep = concatenator.coord_delim

    # A new string is constructed.
    return new_sep.join(
        f'{concatenator.group_delim}{c.replace("/", concatenator.group_delim)}'
        for c in str_with_groups.split()  # split on any whitespace
    )


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
