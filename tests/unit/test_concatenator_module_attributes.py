import pytest

import concatenator


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
