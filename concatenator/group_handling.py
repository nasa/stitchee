"""
group_handling.py

Functions for converting multidimensional data structures
 between a group hierarchy and a flat structure
"""
import re
from typing import List, Tuple

import netCDF4 as nc
import numpy as np
import xarray as xr

GROUP_DELIM = '__'

COORD_DELIM = "  "

_string_dimension_name_pattern = re.compile("__char[0-9]+")


def walk(group_node: nc.Group,
         path: str,
         new_dataset: nc.Dataset,
         dimensions_dict_to_populate: dict,
         list_of_character_string_vars: list):
    """Recursive function to step through each group and subgroup."""
    for key, item in group_node.items():
        group_path = f'{path}{GROUP_DELIM}{key}'

        if item.dimensions:
            dims = list(item.dimensions.keys())
            for dim_name in dims:
                new_dim_name = f'{group_path.replace("/", GROUP_DELIM)}{GROUP_DELIM}{dim_name}'
                item.dimensions[new_dim_name] = item.dimensions[dim_name]
                dimensions_dict_to_populate[new_dim_name] = item.dimensions[dim_name]
                item.renameDimension(dim_name, new_dim_name)

        # If there are variables in this group, copy to root group
        # and then delete from current group
        if item.variables:
            # Copy variables to root group with new name
            for var_name, var in item.variables.items():

                if var_name == "imager_addl_central_wavelength":
                    print("DEBUGing")
                    pass

                var_group_name = f'{group_path}{GROUP_DELIM}{var_name}'
                new_dataset.variables[var_group_name] = var

                # Flatten the paths of variables referenced in the coordinates attribute.
                if 'coordinates' in var.ncattrs():
                    coord_att = var.getncattr('coordinates')
                    new_dataset.variables[var_group_name].setncattr('coordinates',
                                                                    _flatten_coordinate_attribute(coord_att))

                if (len(var.dimensions) == 1) and _string_dimension_name_pattern.fullmatch(var.dimensions[0]):
                    list_of_character_string_vars.append(var_group_name)

            # Delete variables
            temp_copy_for_iterating = list(item.variables.keys())
            for var_name in temp_copy_for_iterating:
                del item.variables[var_name]

        # If there are subgroups in this group, call this function
        # again on that group.
        if item.groups:
            walk(item.groups, group_path, new_dataset, dimensions_dict_to_populate, list_of_character_string_vars)

    # Delete non-root groups
    group_names = list(group_node.keys())
    for group_name in group_names:
        del group_node[group_name]


def flatten_grouped_dataset(nc_dataset: nc.Dataset,
                            file_to_subset: str,
                            ensure_all_dims_are_coords: bool = False
                            ) -> Tuple[nc.Dataset, List[str], List[str]]:
    """
    Transform a netCDF4 Dataset that has groups to an xarray compatible
    dataset. xarray does not work with groups, so this transformation
    will flatten the variables in the dataset and use the group path as
    the new variable name. For example, data_01 > km > sst would become
    'data_01__km__sst', where GROUP_DELIM is __.

    This same pattern is applied to dimensions, which are located under
    the appropriate group. They are renamed and placed in the root
    group.

    Parameters
    ----------
    nc_dataset : nc.Dataset
        netCDF4 Dataset that contains groups
    file_to_subset : str

    Returns
    -------
    nc.Dataset
        netCDF4 Dataset that does not contain groups and that has been
        flattened.
    """
    # Close the existing read-only dataset and reopen in append mode
    nc_dataset.close()
    nc_dataset = nc.Dataset(file_to_subset, 'r+')

    dimensions = {}

    # for var_name in list(nc_dataset.variables.keys()):
    #     new_var_name = f'{GROUP_DELIM}{var_name}'
    #     nc_dataset.variables[new_var_name] = nc_dataset.variables[var_name]
    #     del nc_dataset.variables[var_name]

    if nc_dataset.variables:
        temp_copy_for_iterating = list(nc_dataset.variables.items())
        for var_name, var in temp_copy_for_iterating:
            new_var_name = f'{GROUP_DELIM}{var_name}'

            # ds_new.variables[new_var_name] = ds_old.variables[var_name]

            # Copy variables to root group with new name
            nc_dataset.variables[new_var_name] = var

            # Flatten the paths of variables referenced in the coordinates attribute.
            if 'coordinates' in var.ncattrs():
                coord_att = var.getncattr('coordinates')
                nc_dataset.variables[new_var_name].setncattr('coordinates', _flatten_coordinate_attribute(coord_att))

            del nc_dataset.variables[var_name]  # Delete old variable

    temporary_coordinate_variables = []
    if nc_dataset.dimensions:
        temp_copy_for_iterating = list(nc_dataset.dimensions.keys())
        for dim_name in temp_copy_for_iterating:
            new_dim_name = f'{GROUP_DELIM}{dim_name}'
            # dimensions[new_dim_name] = item.dimensions[dim_name]
            # item.renameDimension(dim_name, new_dim_name)
            # ds_new.dimensions[new_dim_name] = item.dimensions[dim_name]
            dim = nc_dataset.dimensions[dim_name]

            dimensions[new_dim_name] = dim
            nc_dataset.renameDimension(dim_name, new_dim_name)

            # Create a coordinate variable, if it doesn't already exist.
            if ensure_all_dims_are_coords and (new_dim_name not in list(nc_dataset.variables.keys())):
                print(f"Creating coordinate variable for {new_dim_name}...")
                nc_dataset.createVariable(dim.name, datatype=np.int32, dimensions=(dim.name,))
                temporary_coordinate_variables.append(dim.name)

    list_of_character_string_vars: list[str] = []
    walk(nc_dataset.groups, '', nc_dataset, dimensions, list_of_character_string_vars)

    # Update the dimensions of the dataset in the root group
    nc_dataset.dimensions.update(dimensions)

    return nc_dataset, temporary_coordinate_variables, list_of_character_string_vars


def regroup_flattened_dataset(dataset: xr.Dataset, output_file: str) -> None:  # pylint: disable=too-many-branches
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
    """

    with nc.Dataset(output_file, mode='w', format='NETCDF4') as base_dataset:
        # Copy global attributes
        base_dataset.setncatts(dataset.attrs)

        # Create Groups
        group_lst = []
        for var_name, _ in dataset.variables.items():  # need logic if there is data in the top level not in a group
            group_lst.append('/'.join(var_name.split(GROUP_DELIM)[:-1]))
        group_lst = ['/' if group == '' else group for group in group_lst]
        groups = set(group_lst)
        for group in groups:
            base_dataset.createGroup(group)

        # Copy dimensions
        for dim_name, _ in dataset.dims.items():
            new_dim_name = dim_name.split(GROUP_DELIM)[-1]
            dim_group = _get_nested_group(base_dataset, dim_name)
            dim_group.createDimension(new_dim_name, dataset.dims[dim_name])
            # dst.createDimension(
            #     name, (len(dimension) if not dimension.isunlimited() else None))

        # Copy variables
        for var_name, var in dataset.variables.items():
            new_var_name = var_name.split(GROUP_DELIM)[-1]
            var_group = _get_nested_group(base_dataset, var_name)
            # grouping = '/'.join(var_name.split(GROUP_DELIM)[:-1])
            try:
                this_dtype = var.dtype
                if np.issubdtype(this_dtype, np.integer):
                    """Only Use Shuffle Filter on Integer Data.
                    See, e.g.: https://www.linkedin.com/pulse/netcdf-4hdf5-only-use-shuffle-filter-integer-data-edward-hartnett/
                    """
                    shuffle = True
                else:
                    shuffle = False

                # Get the fill value (since it's not included in xarray var.attrs)
                try:
                    fill_value = var.encoding['_FillValue'].astype(this_dtype)
                except KeyError:
                    fill_value = None

                # Decide on the dimensions and chunksizes along each dimension
                new_var_dims: tuple
                if isinstance(var, xr.IndexVariable):
                    new_var_dims = (new_var_name,)
                    chunk_sizes = None
                else:
                    new_var_dims = tuple(d.split(GROUP_DELIM)[-1] for d in var.dims)
                    dim_sizes = [_get_dimension_size(base_dataset, dim) for dim in new_var_dims]

                    chunk_sizes = _calculate_chunks(dim_sizes, default_low_dim_chunksize=4000)

                # Do the variable creation
                if var.dtype == "O":
                    vartype = "S1"
                else:
                    vartype = var.dtype
                var_group.createVariable(new_var_name, vartype,
                                         dimensions=new_var_dims, chunksizes=chunk_sizes,
                                         compression='zlib', complevel=7,
                                         shuffle=shuffle, fill_value=fill_value)

                # copy variable attributes all at once via dictionary
                var_group[new_var_name].setncatts(var.attrs)
                # copy variable values
                var_group[new_var_name][:] = var.values

                # Reconstruct the grouped paths of variables referenced in the coordinates attribute.
                if 'coordinates' in var_group[new_var_name].ncattrs():
                    coord_att = var_group[new_var_name].getncattr('coordinates')
                    var_group[new_var_name].setncattr('coordinates', _regroup_coordinate_attribute(coord_att))

            except Exception as err:
                raise err


def _get_nested_group(dataset: nc.Dataset, group_path: str) -> nc.Group:
    nested_group = dataset
    for group in group_path.strip(GROUP_DELIM).split(GROUP_DELIM)[:-1]:
        nested_group = nested_group.groups[group]
    return nested_group


def _flatten_coordinate_attribute(attribute_string: str) -> str:
    """
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
    return COORD_DELIM.join(
        f'{GROUP_DELIM}{c.replace("/", GROUP_DELIM)}'
        for c
        in attribute_string.split(COORD_DELIM)
    )


def _regroup_coordinate_attribute(attribute_string: str) -> str:
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
    return COORD_DELIM.join(
        '/'.join(c.split(GROUP_DELIM))[1:]
        for c
        in attribute_string.split(COORD_DELIM)
    )


def _calculate_chunks(dim_sizes: list, default_low_dim_chunksize=4000) -> tuple:
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
        chunk_sizes = tuple(default_low_dim_chunksize
                            if ((s > default_low_dim_chunksize) and (number_of_dims > 1))
                            else s
                            for s in dim_sizes
                            )
    else:
        chunk_sizes = tuple(500 if s > 500
                            else s
                            for s in dim_sizes
                            )

    return chunk_sizes


def _get_dimension_size(nc_Dataset: nc.Dataset, dim_name: str) -> int:
    # Determine if the dimension is defined at the root level
    if dim_name in nc_Dataset.dimensions.keys():
        dim_size = nc_Dataset.dimensions[dim_name].size

    # Search groups if dim_name is not found at the root level
    else:
        dim_size = None
        # loop through groups until the dimension name is found
        for grp in nc_Dataset.groups.keys():
            if dim_name in nc_Dataset.groups[grp].dimensions.keys():
                dim_size = nc_Dataset.groups[grp].dimensions[dim_name].size
                break

    if dim_size is None:
        print(f"Dimension {dim_name} not found when searching for sizes!")
    return dim_size
