"""Tests for manipulating netCDF groups."""

# pylint: disable=C0116, C0301

from concatenator.attribute_handling import (_flatten_coordinate_attribute,
                                             regroup_coordinate_attribute)


def test_coordinate_attribute_flattening():
    # Case with groups present and double spaces.
    assert _flatten_coordinate_attribute(
        "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"
    ) == '__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude'

    # Case with NO groups present and single spaces.
    assert _flatten_coordinate_attribute(
        "time longitude latitude ozone_profile_pressure ozone_profile_altitude"
    ) == "__time __longitude __latitude __ozone_profile_pressure __ozone_profile_altitude"


def test_coordinate_attribute_regrouping():
    # Case with groups present and double spaces.
    assert regroup_coordinate_attribute(
        '__Time_and_Position__time  __Time_and_Position__instrument_fov_latitude  __Time_and_Position__instrument_fov_longitude') == "Time_and_Position/time  Time_and_Position/instrument_fov_latitude  Time_and_Position/instrument_fov_longitude"

    # Case with NO groups present and single spaces.
    assert regroup_coordinate_attribute(
        "__time __longitude __latitude __ozone_profile_pressure __ozone_profile_altitude") == "time longitude latitude ozone_profile_pressure ozone_profile_altitude"
