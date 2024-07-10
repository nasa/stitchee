import pytest

import concatenator
from concatenator.attribute_handling import (
    flatten_string_with_groups,
    regroup_coordinate_attribute,
)


def test_coordinate_attribute_flattening():
    # Case with groups present and double spaces.
    assert (
        flatten_string_with_groups(
            "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
        )
        == "__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude"
    )

    # Case with NO groups present and single spaces.
    assert (
        flatten_string_with_groups(
            "time longitude latitude ozone_profile_pressure ozone_profile_altitude"
        )
        == "__time __longitude __latitude __ozone_profile_pressure __ozone_profile_altitude"
    )


def test_variable_path_flattening():
    # Case with group present.
    assert flatten_string_with_groups("geolocation/time") == "__geolocation__time"

    # Case with NO groups present.
    assert flatten_string_with_groups("time") == "__time"


def test_coordinate_attribute_regrouping():
    # Case with groups present and double spaces.
    assert (
        regroup_coordinate_attribute(
            "__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude"
        )
        == "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
    )

    # Case with NO groups present and single spaces.
    assert (
        regroup_coordinate_attribute(
            "__time __longitude __latitude __ozone_profile_pressure __ozone_profile_altitude"
        )
        == "time longitude latitude ozone_profile_pressure ozone_profile_altitude"
    )


def test_concatenator_options_getting_and_setting():
    """Test setting attributes for the concatenator module.

    Note that currently, new attributes can be defined dynamically.
    Note also, that attributes must be reset before further testing because they are global.
    """
    default_group_delim = "__"
    assert concatenator.group_delim == default_group_delim
    concatenator.group_delim = "%"
    assert concatenator.group_delim == "%"
    concatenator.group_delim = default_group_delim
    assert concatenator.group_delim == default_group_delim

    default_coord_delim = "  "
    assert concatenator.coord_delim == default_coord_delim
    concatenator.coord_delim = "---"
    assert concatenator.coord_delim == "---"
    concatenator.coord_delim = default_coord_delim
    assert concatenator.coord_delim == default_coord_delim

    concatenator.nonexistent_attribute = "---"
    assert concatenator.nonexistent_attribute == "---"
    del concatenator.nonexistent_attribute
    with pytest.raises(AttributeError):
        _ = concatenator.nonexistent_attribute
