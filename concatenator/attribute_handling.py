"""
attribute_handling.py

Functions for converting "coordinates" in netCDF variable attributes
 between paths that reference a group hierarchy and flattened paths.
"""

import json
import re
from datetime import datetime, timezone

import importlib_metadata
import netCDF4
import xarray as xr

from concatenator import COORD_DELIM, GROUP_DELIM

# Values needed for history_json attribute
HISTORY_JSON_SCHEMA = "https://harmony.earthdata.nasa.gov/schemas/history/0.1.0/history-v0.1.0.json"
PROGRAM = "stitchee"
PROGRAM_REF = "https://cmr.earthdata.nasa.gov:443/search/concepts/S1262025641-LARC_CLOUD"
VERSION = importlib_metadata.distribution("stitchee").version


def regroup_coordinate_attribute(attribute_string: str) -> str:
    """
    Examples
    --------
    >>> coord_att = "__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude"
    >>> _flatten_coordinate_attribute(coord_att)
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
        new_sep = COORD_DELIM

    return new_sep.join(
        "/".join(c.split(GROUP_DELIM))[1:]
        for c in attribute_string.split()  # split on any whitespace
    )


def flatten_coordinate_attribute_paths(
    dataset: netCDF4.Dataset, var: netCDF4.Variable, variable_name: str
) -> None:
    """Flatten the paths of variables referenced in the coordinates attribute."""
    if "coordinates" in var.ncattrs():
        coord_att = var.getncattr("coordinates")

        new_coord_att = _flatten_coordinate_attribute(coord_att)

        dataset.variables[variable_name].setncattr("coordinates", new_coord_att)


def _flatten_coordinate_attribute(attribute_string: str) -> str:
    """Converts attributes that specify group membership via "/" to use new group delimiter, even for the root level.

    Examples
    --------
    >>> coord_att = "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
    >>> _flatten_coordinate_attribute(coord_att)
        __Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude

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
        new_sep = COORD_DELIM

    # A new string is constructed.
    return new_sep.join(
        f'{GROUP_DELIM}{c.replace("/", GROUP_DELIM)}'
        for c in attribute_string.split()  # split on any whitespace
    )


def create_new_attributes(input_dataset: xr.Dataset, request_parameters: dict) -> dict:
    """Set the global attributes of the merged output file.

    These begin as the global attributes of the input granule, but are updated to also include
    the provenance data via an updated `history` CF attribute (or `History`
    if that is already present), and a `history_json` attribute that is
    compliant with the schema defined at the URL specified by
    `HISTORY_JSON_SCHEMA`.

    `projection` is not included in the output parameters, as this is not
    an original message parameter. It is a derived `pyproj.Proj` instance
    that is defined by the input `crs` parameter.

    `x_extent` and `y_extent` are not serializable, and are instead
    included by `x_min`, `x_max` and `y_min` `y_max` accordingly.

    Parameters
    ----------
    input_dataset : Dataset
    request_parameters : dict
    """
    # Get attributes from input file
    output_attributes = input_dataset.attrs

    # Reconstruct parameters' dictionary with only keys that correspond to non-null values.
    valid_request_parameters = {
        parameter_name: parameter_value
        for parameter_name, parameter_value in request_parameters.items()
        if parameter_value is not None
    }

    # Remove unnecessary and unserializable request parameters
    for surplus_key in ["projection", "x_extent", "y_extent"]:
        valid_request_parameters.pop(surplus_key, None)

    # Retrieve `granule_url` and replace the `input_file` attribute.
    # This ensures `history_json` refers to the archived granule location, rather
    # than a temporary file in the Docker container.
    valid_request_parameters["input_file"] = valid_request_parameters.pop("granule_url", None)

    # Preferentially use `history`, unless `History` is already present in the
    # input file.
    cf_att_name = "History" if hasattr(input_dataset, "History") else "history"
    input_history = getattr(input_dataset, cf_att_name, None)

    # Create new history_json attribute
    new_history_json_record = create_history_record(str(input_history), valid_request_parameters)

    # Extract existing `history_json` from input granule
    if hasattr(input_dataset, "history_json"):
        old_history_json = json.loads(output_attributes["history_json"])
        if isinstance(old_history_json, list):
            output_history_json = old_history_json
        else:
            # Single `history_record` element.
            output_history_json = [old_history_json]
    else:
        output_history_json = []

    # Append `history_record` to the existing `history_json` array:
    output_history_json.append(new_history_json_record)
    output_attributes["history_json"] = json.dumps(output_history_json)

    # Create history attribute
    history_parameters = {
        parameter_name: parameter_value
        for parameter_name, parameter_value in new_history_json_record["parameters"].items()
        if parameter_name != "input_file"
    }

    new_history_line = " ".join(
        [
            new_history_json_record["date_time"],
            new_history_json_record["program"],
            new_history_json_record["version"],
            json.dumps(history_parameters),
        ]
    )

    output_history = "\n".join(filter(None, [input_history, new_history_line]))
    output_attributes[cf_att_name] = output_history

    return output_attributes


def create_history_record(input_history: str, request_parameters: dict) -> dict:
    """Create a serializable dictionary for the `history_json` global
    attribute in the merged output NetCDF-4 file.

    """
    history_record = {
        "$schema": HISTORY_JSON_SCHEMA,
        "date_time": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "program": PROGRAM,
        "version": VERSION,
        "parameters": request_parameters,
        "derived_from": request_parameters["input_file"],
        "program_ref": PROGRAM_REF,
    }

    if isinstance(input_history, str):
        history_record["cf_history"] = input_history.split("\n")
    elif isinstance(input_history, list):
        history_record["cf_history"] = input_history

    return history_record


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
