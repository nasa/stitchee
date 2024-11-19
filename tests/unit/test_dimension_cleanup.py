"""Tests for netCDF dimension clean up operations."""

# pylint: disable=C0116, C0301

import netCDF4 as nc

from concatenator.dimension_cleanup import (
    get_attributes_minus_fillvalue_and_renamed_coords,
)


def test_get_attributes_minus_fillvalue_and_renamed_coords(ds_3dims_3vars_2coords_nogroup):
    with nc.Dataset(ds_3dims_3vars_2coords_nogroup, "r+") as ds:
        attr_contents_dict = get_attributes_minus_fillvalue_and_renamed_coords(
            original_var_name="var0", new_var_name="new_dim", original_dataset=ds
        )

        assert attr_contents_dict["coordinates"] == "new_dim track"


# TODO: this next test is still failing.
#  Should go away once using xarray's DataTree instead of flattening group structure.
# def test_remove_duplicate_dims(ds_3dims_3vars_2coords_nogroup_duplicate_dimensions):
#     with nc.Dataset(ds_3dims_3vars_2coords_nogroup_duplicate_dimensions, "r+") as ds:
#         ds_with_replaced_dims = remove_duplicate_dims(ds)
#
#         ds_with_replaced_dims["var0"].coordinates = "var0 track track"
#
#         assert ds_with_replaced_dims["var0"].coordinates == "var0 track track_1"
