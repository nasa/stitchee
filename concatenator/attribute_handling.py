"""
attribute_handling.py

Functions for converting "coordinates" in netCDF variable attributes
 between paths that reference a group hierarchy and flattened paths.
"""
import re

import netCDF4

from concatenator import COORD_DELIM, GROUP_DELIM


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
    """Converts attributes with "/" delimiters to use new group delimiter, even for the root level.

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
    if len(set(whitespaces)) == 1:
        new_sep = whitespaces[0]
    else:
        new_sep = COORD_DELIM

    # A new string is constructed.
    return new_sep.join(flatten_variable_path_str(item) for item in attribute_string.split())


def flatten_variable_path_str(path_str: str) -> str:
    """Converts a path with "/" delimiters to use new group delimiter, even for the root level."""
    new_path = path_str.replace("/", GROUP_DELIM)

    return f"{GROUP_DELIM}{new_path}" if not new_path.startswith(GROUP_DELIM) else new_path
