import pytest
import numpy as np
import xarray as xr

from stitchee.concatenate import (
    _find_variables_with_duplicate_dimensions,
    _rename_to_uniq_dimensions,
    _concat_with_duplicate_dims,
)


@pytest.fixture
def dataset():
    nstep, nxtrack, nlayer, nlevel = 4, 5, 6, 3

    # Coordinate labels
    coords = {
        "mirror_step": np.arange(nstep),
        "xtrack": np.arange(nxtrack),
        "layer": np.arange(nlayer),
        "level": np.arange(nlevel),
    }

    # Variables
    data_vars = {
        # 2D variable
        "var2d": (("mirror_step", "xtrack"), np.random.rand(nstep, nxtrack)),
        # 3D variables
        "var3d_a": (("mirror_step", "xtrack", "layer"), np.random.rand(nstep, nxtrack, nlayer)),
        "var3d_b": (("mirror_step", "layer", "layer"), np.random.rand(nstep, nlayer, nlayer)),
        "var3d_c": (("mirro_step", "xtrack", "level"), np.random.rand(nstep, nxtrack, nlevel)),
        # 4D variables
        "var4d_a": (
            ("mirror_step", "xtrack", "layer", "layer"),
            np.random.rand(nstep, nxtrack, nlayer, nlayer),
        ),
        "var4d_b": (
            ("mirror_step", "xtrack", "layer", "level"),
            np.random.rand(nstep, nxtrack, nlayer, nlevel),
        ),
    }

    # Build dataset
    return xr.Dataset(data_vars=data_vars, coords=coords)


def test_finding_variables_with_duplicate_dimensions(dataset):
    duplicate_variables = _find_variables_with_duplicate_dimensions(dataset)
    assert duplicate_variables == ["var3d_b", "var4d_a"]


def test_renaming_to_uniq_dimensions(dataset):
    new_dataset4d = _rename_to_uniq_dimensions(dataset["var4d_a"])
    assert new_dataset4d.dims == ("mirror_step", "xtrack", "layer", "1___layer")


def test_concat_with_duplicate_dims():
    data4d_1 = np.random.rand(20, 30, 5, 5)
    da_1 = xr.DataArray(
        data4d_1,
        dims=("mirror_step", "xtrack", "layer", "layer"),
        coords={"mirror_step": np.arange(20), "xtrack": np.arange(30), "layer": np.arange(5)},
        name="var4d",
    )

    data4d_2 = np.random.rand(11, 30, 5, 5)
    da_2 = xr.DataArray(
        data4d_2,
        dims=("mirror_step", "xtrack", "layer", "layer"),
        coords={"mirror_step": np.arange(20, 31), "xtrack": np.arange(30), "layer": np.arange(5)},
        name="var4d",
    )

    total_da = xr.DataArray(
        np.concatenate([data4d_1, data4d_2], axis=0),
        dims=("mirror_step", "xtrack", "layer", "layer"),
        coords={"mirror_step": np.arange(31), "xtrack": np.arange(30), "layer": np.arange(5)},
        name="var4d",
    )

    concat_kwargs = {"data_vars": "minimal", "coords": "minimal", "compat": "override"}

    concatenated_da = _concat_with_duplicate_dims(
        [da_1, da_2], concat_dim="mirror_step", concat_kwargs=concat_kwargs
    )

    assert total_da.identical(concatenated_da)
