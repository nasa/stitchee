"""Functions to convert data structures between a group hierarchy and a flat structure."""

from __future__ import annotations

import logging
import re
from logging import Logger

import netCDF4 as nc
import numpy as np
import xarray as xr

import concatenator
from concatenator.attribute_handling import (
    flatten_coordinate_attribute_paths,
    regroup_coordinate_attribute,
)

module_logger = logging.getLogger(__name__)

# Match dimension names such as "__char28" or "__char16". Used for CERES datasets.
_string_dimension_name_pattern = re.compile(r"__char[0-9]+")


def walk(
    group_node: nc.Group,
    path: str,
    new_dataset: nc.Dataset,
    dimensions_dict_to_populate: dict,
    list_of_character_string_vars: list,
):
    """Recursive function to step through each group and subgroup."""
    for key, item in group_node.items():
        group_path = f"{path}{concatenator.group_delim}{key}"

        if item.dimensions:
            dims = list(item.dimensions.keys())
            for dim_name in dims:
                new_dim_name = f"{group_path.replace('/', concatenator.group_delim)}{concatenator.group_delim}{dim_name}"
                item.dimensions[new_dim_name] = item.dimensions[dim_name]
                dimensions_dict_to_populate[new_dim_name] = item.dimensions[dim_name]
                item.renameDimension(dim_name, new_dim_name)

        # If there are variables in this group, copy to root group
        # and then delete from current group
        if item.variables:
            # Copy variables to root group with new name
            for var_name, var in item.variables.items():
                var_group_name = f"{group_path}{concatenator.group_delim}{var_name}"
                new_dataset.variables[var_group_name] = var

                # Flatten the paths of variables referenced in the 'coordinates' attribute
                flatten_coordinate_attribute_paths(new_dataset, var, var_group_name)

                if (len(var.dimensions) == 1) and _string_dimension_name_pattern.fullmatch(
                    var.dimensions[0]
                ):
                    list_of_character_string_vars.append(var_group_name)

            # Delete variables
            temp_copy_for_iterating = list(item.variables.keys())
            for var_name in temp_copy_for_iterating:
                del item.variables[var_name]

        # If there are subgroups in this group, call this function
        # again on that group.
        if item.groups:
            walk(
                item.groups,
                group_path,
                new_dataset,
                dimensions_dict_to_populate,
                list_of_character_string_vars,
            )

    # Delete non-root groups
    group_names = list(group_node.keys())
    for group_name in group_names:
        del group_node[group_name]


def flatten_grouped_dataset(
    nc_dataset: nc.Dataset, ensure_all_dims_are_coords: bool = False
) -> tuple[nc.Dataset, list[str], list[str]]:
    """
    Transform a netCDF4 Dataset that has groups to an xarray compatible
    dataset. xarray does not work with groups, so this transformation
    will flatten the variables in the dataset and use the group path as
    the new variable name. For example, data_01 > km > sst would become
    'data_01__km__sst', where concatenator.group_delim is __.

    This same pattern is applied to dimensions, which are located under
    the appropriate group. They are renamed and placed in the root
    group.

    Parameters
    ----------
    nc_dataset : nc.Dataset
        netCDF4 Dataset that contains groups
    ensure_all_dims_are_coords

    Returns
    -------
    nc.Dataset
        netCDF4 Dataset that does not contain groups and that has been
        flattened.
    """

    dimensions = {}

    # for var_name in list(nc_dataset.variables.keys()):
    #     new_var_name = f'{concatenator.group_delim}{var_name}'
    #     nc_dataset.variables[new_var_name] = nc_dataset.variables[var_name]
    #     del nc_dataset.variables[var_name]

    if nc_dataset.variables:
        temp_copy_for_iterating = list(nc_dataset.variables.items())
        for var_name, var in temp_copy_for_iterating:
            new_var_name = f"{concatenator.group_delim}{var_name}"

            # ds_new.variables[new_var_name] = ds_old.variables[var_name]

            # Copy variables to root group with new name
            nc_dataset.variables[new_var_name] = var

            # Flatten the paths of variables referenced in the 'coordinates' attribute.
            flatten_coordinate_attribute_paths(nc_dataset, var, new_var_name)

            del nc_dataset.variables[var_name]  # Delete old variable

    temporary_coordinate_variables = []
    if nc_dataset.dimensions:
        temp_copy_for_iterating = list(nc_dataset.dimensions.keys())
        for dim_name in temp_copy_for_iterating:
            new_dim_name = f"{concatenator.group_delim}{dim_name}"
            # dimensions[new_dim_name] = item.dimensions[dim_name]
            # item.renameDimension(dim_name, new_dim_name)
            # ds_new.dimensions[new_dim_name] = item.dimensions[dim_name]
            dim = nc_dataset.dimensions[dim_name]

            dimensions[new_dim_name] = dim
            nc_dataset.renameDimension(dim_name, new_dim_name)

            # Create a coordinate variable, if it doesn't already exist.
            if ensure_all_dims_are_coords and (
                new_dim_name not in list(nc_dataset.variables.keys())
            ):
                nc_dataset.createVariable(dim.name, datatype=np.int32, dimensions=(dim.name,))
                temporary_coordinate_variables.append(dim.name)

    list_of_character_string_vars: list[str] = []
    walk(nc_dataset.groups, "", nc_dataset, dimensions, list_of_character_string_vars)

    # Update the dimensions of the dataset in the root group
    nc_dataset.dimensions.update(dimensions)

    return nc_dataset, temporary_coordinate_variables, list_of_character_string_vars


def regroup_flattened_dataset(
    dataset: xr.Dataset, output_file: str, history_to_append: str | None
) -> None:  # pylint: disable=too-many-branches
    """
    Given a list of xarray datasets, combine those datasets into a
    single netCDF4 Dataset and write to the disk. Each dataset has been
    transformed using its group path and needs to be un-transformed and
    placed in the appropriate group.

    Parameters
    ----------
    dataset : list (xr.Dataset)
        List of xarray datasets to be combined
    output_file : str
        Name of the output file to write the resulting NetCDF file to.
    history_to_append : str
    """
    with nc.Dataset(output_file, mode="w", format="NETCDF4") as base_dataset:
        # Copy global attributes
        output_attributes = dataset.attrs
        if history_to_append is not None:
            output_attributes["history_json"] = history_to_append
        base_dataset.setncatts(output_attributes)

        # Create Groups
        group_lst = []
        # need logic if there is data in the top level not in a group
        for var_name, _ in dataset.variables.items():
            group_lst.append("/".join(str(var_name).split(concatenator.group_delim)[:-1]))
        group_lst = ["/" if group == "" else group for group in group_lst]
        groups = set(group_lst)
        for group in groups:
            base_dataset.createGroup(group)

        # Copy dimensions
        for dim_name, _ in dataset.dims.items():
            new_dim_name = str(dim_name).rsplit(concatenator.group_delim, 1)[-1]
            dim_group = _get_nested_group(base_dataset, str(dim_name))
            dim_group.createDimension(new_dim_name, dataset.sizes[dim_name])
            # dst.createDimension(
            #     name, (len(dimension) if not dimension.isunlimited() else None))

        # Copy variables
        for var_name, var in dataset.variables.items():
            new_var_name = str(var_name).rsplit(concatenator.group_delim, 1)[-1]
            var_group = _get_nested_group(base_dataset, str(var_name))
            # grouping = '/'.join(var_name.split(concatenator.group_delim)[:-1])
            try:
                this_dtype = var.dtype

                # Only Use Shuffle Filter on Integer Data.
                # See, e.g.: https://www.linkedin.com/pulse/netcdf-4hdf5-only-use-shuffle-filter-integer-data-edward-hartnett/
                shuffle = bool(np.issubdtype(this_dtype, np.integer))

                # Get the fill value (since it's not included in xarray var.attrs)
                try:
                    fill_value = var.encoding["_FillValue"].astype(this_dtype)
                except KeyError:
                    fill_value = None

                # Decide on the dimensions and chunksizes along each dimension
                new_var_dims: tuple
                if isinstance(var, xr.IndexVariable):
                    new_var_dims = (new_var_name,)
                    chunk_sizes = None
                else:
                    new_var_dims = tuple(
                        str(d).rsplit(concatenator.group_delim, 1)[-1] for d in var.dims
                    )
                    dim_sizes = [_get_dimension_size(base_dataset, dim) for dim in new_var_dims]

                    chunk_sizes = _calculate_chunks(dim_sizes, default_low_dim_chunksize=4000)

                # Do the variable creation
                if var.dtype == "O":
                    vartype = "S1"
                else:
                    vartype = str(var.dtype)

                compression: str | None = "zlib"
                if vartype.startswith("<U") and len(var.shape) == 1 and var.shape[0] < 10:
                    compression = None

                var_group.createVariable(
                    new_var_name,
                    vartype,
                    dimensions=new_var_dims,
                    chunksizes=chunk_sizes,
                    compression=compression,
                    complevel=7,
                    shuffle=shuffle,
                    fill_value=fill_value,
                )

                # copy variable attributes all at once via dictionary
                var_group[new_var_name].setncatts(var.attrs)
                # copy variable values
                var_group[new_var_name][:] = var.values

                # Reconstruct the grouped paths of variables referenced in the coordinates attribute.
                if "coordinates" in var_group[new_var_name].ncattrs():
                    coord_att = var_group[new_var_name].getncattr("coordinates")
                    var_group[new_var_name].setncattr(
                        "coordinates", regroup_coordinate_attribute(coord_att)
                    )

            except Exception as err:
                raise err


def _get_nested_group(dataset: nc.Dataset, group_path: str) -> nc.Group:
    """Get the group object that is represented by the group_path string.

    If the 'group_path' string represents a dimension in the root group,
    then this returns the root group.
    """
    nested_group = dataset
    for group in group_path.strip(concatenator.group_delim).split(concatenator.group_delim)[:-1]:
        nested_group = nested_group.groups[group]
    return nested_group


def _calculate_chunks(dim_sizes: list, default_low_dim_chunksize: int = 4000) -> tuple:
    """
    For the given dataset, calculate if the size on any dimension is
    worth chunking. Any dimension larger than 4000 will be chunked. This
    is done to ensure that the variable can fit in memory.
    Parameters
    ----------
    dim_sizes
        The length of each dimension

    Returns
    -------
    tuple
        The chunk size, where each element is a dimension and the
        value is 4000 or 500 depending on how many dimensions.
    """
    number_of_dims = len(dim_sizes)
    if number_of_dims <= 3:
        chunk_sizes = tuple(
            (
                default_low_dim_chunksize
                if ((s > default_low_dim_chunksize) and (number_of_dims > 1))
                else s
            )
            for s in dim_sizes
        )
    else:
        chunk_sizes = tuple(500 if s > 500 else s for s in dim_sizes)

    return chunk_sizes


def _get_dimension_size(dataset: nc.Dataset, dim_name: str) -> int:
    # Determine if the dimension is defined at the root level
    if dim_name in dataset.dimensions.keys():
        dim_size = dataset.dimensions[dim_name].size

    # Search groups if dim_name is not found at the root level
    else:
        dim_size = None
        # loop through groups until the dimension name is found
        for grp in dataset.groups.keys():
            if dim_name in dataset.groups[grp].dimensions.keys():
                dim_size = dataset.groups[grp].dimensions[dim_name].size
                break

    if dim_size is None:
        print(f"Dimension {dim_name} not found when searching for sizes!")
    return dim_size


def validate_workable_files(
    files: list[str], logger: Logger | None = module_logger
) -> tuple[list[str], int]:
    """Remove files from a list that are not open-able as netCDF or that are empty."""
    workable_files = []
    for file in files:
        try:
            with nc.Dataset(file, "r") as dataset:
                is_empty = _is_file_empty(dataset)
                if is_empty is False:
                    workable_files.append(file)
        except OSError:
            if logger:
                logger.debug("Error opening <%s> as a netCDF dataset. Skipping.", file)
            else:
                print("Error opening <%s> as a netCDF dataset. Skipping.")

    # addressing GitHub issue 153: propagate the first empty file if all input files are empty
    if (len(workable_files)) == 0 and (len(files) > 0):
        workable_files.append(files[0])

    number_of_workable_files = len(workable_files)

    return workable_files, number_of_workable_files


def _is_file_empty(parent_group: nc.Dataset | nc.Group) -> bool:
    """Check if netCDF dataset is empty or not.

    Tests if all variable arrays are empty.
    As soon as a variable is detected with both (i) an array size not equal to zero and
    (ii) not all null/fill values, then the granule is considered non-empty.

    Returns
    -------
    False if the dataset is considered non-empty; True otherwise (dataset is indeed empty).
    """
    for var_name, var in parent_group.variables.items():
        if var.size != 0:
            if "_FillValue" in var.ncattrs():
                fill_or_null = getattr(var, "_FillValue")
            else:
                fill_or_null = np.nan

            # This checks three ways that the variable's array might be considered empty.
            # If none of the ways are true,
            #   a non-empty variable has been found and False is returned.
            # If one of the ways is true, we consider the variable empty,
            #   and continue checking other variables.
            empty_way_1 = False
            if np.ma.isMaskedArray(var[:]):
                empty_way_1 = var[:].mask.all()
            empty_way_2 = np.all(var[:].data == fill_or_null)
            empty_way_3 = np.all(np.isnan(var[:].data))

            if not (empty_way_1 or empty_way_2 or empty_way_3):
                return False  # Found a non-empty variable.

    for child_group in parent_group.groups.values():
        return _is_file_empty(child_group)
    return True
