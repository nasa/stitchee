"""Concatenation service that appends data along an existing dimension, using netCDF4 and xarray."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from functools import partial
from logging import Logger
from warnings import warn

import xarray as xr

from stitchee.file_ops import (
    validate_input_path,
    validate_output_path,
    validate_workable_files,
)

# Module constants
SUPPORTED_CONCAT_METHODS = ("xarray-concat", "xarray-combine")
# include compat="override" to handle inconsistent values of gas_names in O3PROF collection
DEFAULT_XARRAY_SETTINGS = {"data_vars": "minimal", "coords": "minimal", "compat": "override"}
DATATREE_OPEN_OPTIONS = {
    "decode_times": False,
    "decode_coords": False,
    "mask_and_scale": False,
}

default_logger = logging.getLogger(__name__)


def concatenate(
    files_to_concat: list[str],
    output_file: str,
    concat_method: str = "xarray-concat",
    concat_dim: str = "",
    concat_kwargs: dict | None = None,
    sorting_variable: str | None = None,
    history_to_append: str | None = None,
    overwrite_output_file: bool = False,
    logger: Logger = default_logger,
) -> str:
    """Concatenate netCDF data files along an existing dimension.

    Parameters
    ----------
    files_to_concat
        netCDF files to concatenate
    output_file
        file path for output file
    concat_method
        concatenation method, either "xarray-concat" (default) or "xarray-combine".
    concat_dim
        dimension along which to concatenate (default: "").
        Not needed if concat_method is "xarray-combine".
    concat_kwargs
        keyword arguments to pass to xarray.concat or xarray.combine_by_coords (default: None).
    sorting_variable
        name of a variable to use for sorting datasets before concatenation (e.g., `time`).
    history_to_append
        JSON string to append to the history attribute of the concatenated file (default: None).
    overwrite_output_file
        whether to overwrite output file if it exists (default: False).
    logger
        logger instance for output messages

    Returns
    -------
    str
        path of concatenated file, empty string if no workable files found
    """
    # Validate inputs
    if not files_to_concat:
        raise ValueError("files_to_concat cannot be empty")
    validate_input_path(files_to_concat)

    # Create concatenation function with validation
    concat_function = _create_concat_function(concat_method, concat_dim, concat_kwargs or {})

    # Get workable files
    input_files, num_input_files = validate_workable_files(files_to_concat, logger)

    # Handle zero or single file cases
    if num_input_files == 0:
        logger.info("No non-empty netCDF files found.")
        return ""

    output_file = validate_output_path(output_file, overwrite=overwrite_output_file)

    if num_input_files == 1:
        xr.open_datatree(input_files[0]).to_netcdf(output_file)
        logger.info("Single workable file, copied to output path without modification.")
        return output_file

    # Process and concatenate multiple files.
    try:
        start_time = time.time()

        # Load, validate, and sort datatrees
        datatree_list = _load_and_sort_datatrees(input_files, sorting_variable, logger)

        # Concatenate files
        logger.info("Concatenating %d files...", len(datatree_list))
        output_tree = _concatenate_datatrees(datatree_list, concat_function)

        # Write output
        _finalize_output(output_tree, output_file, history_to_append)

        logger.info("Completed in %.2f seconds", time.time() - start_time)
        return output_file

    except Exception as err:
        logger.error("Concatenation failed: %s", err)
        raise


def validate_concat_method_and_dim(concat_method: str, concat_dim: str | None = None) -> None:
    """Validate concatenation method and dimension requirements."""
    # Validate method is supported
    if concat_method not in SUPPORTED_CONCAT_METHODS:
        raise ValueError(
            f"Unexpected concatenation method '{concat_method}'. "
            f"Supported methods: {SUPPORTED_CONCAT_METHODS}"
        )

    # Validate method-specific requirements
    if concat_method == "xarray-concat" and not concat_dim:
        raise ValueError(
            "concat_dim is required when using 'xarray-concat' method. "
            "Specify concat_dim or use 'xarray-combine' method instead"
        )

    # Warn about unused parameter
    if concat_method == "xarray-combine" and concat_dim:
        warn(
            "'concat_dim' was specified but will not be used "
            "because 'xarray-combine' method was selected.",
            stacklevel=2,
        )


def _find_variables_with_duplicate_dimensions(dataset: xr.DataSet):
    """Return variable names that have repeated dimensions."""
    duplicate_variables = [
        varname
        for varname in dataset.variables
        if (dims := dataset[varname].dims) and len(dims) != len(set(dims))
    ]

    return duplicate_variables


def _rename_to_uniq_dimensions(dataarray: xr.DataArray):
    """Make duplicate dimension names unique by adding numeric prefixes.

    Returns
    -------
    xr.DataArray
        New DataArray with unique dimension names and updated coordinates.

    Examples
    --------
    >>> arr = xr.DataArray([[1, 2], [3, 4]], dims=['x', 'x'])
    >>> result = _rename_to_uniq_dimensions(arr)
    >>> result.dims
    ('x', '1___x')
    """
    iduplicates = [idim - dataarray.dims.index(dim) for idim, dim in enumerate(dataarray.dims)]
    # rename repeated dimensions with a prefix to each repeated dimension
    new_dims = [
        dim if idup == 0 else f"{idup}___{dim}"
        for idup, dim in zip(iduplicates, dataarray.dims, strict=False)
    ]
    dim_tuple = list(zip(dataarray.dims, new_dims, strict=False))
    # update coordinates with newly renamed dimensions
    new_coords = {
        new_dim: dataarray.coords[old_dim].rename({old_dim: new_dim})
        for old_dim, new_dim in dim_tuple
        if old_dim in dataarray.coords
    }

    # construct new DataArray with repeated dimensions
    new_dataarray = xr.DataArray(
        dataarray.to_numpy(),
        dims=new_dims,
        coords=new_coords,
        name=dataarray.name,
        attrs=dataarray.attrs,
    )

    return new_dataarray


def _concat_with_duplicate_dims(
    dataarrays: list[xr.DataArray], concat_dim: str, concat_kwargs: dict
):
    """Concatenate DataArrays that may have duplicate dimension names.

    Temporarily renames duplicate dimensions, concatenates, then restores original names.
    """
    # Prepare concatenation settings
    # data_vars must be "all" when concatenating because there is only one data_var, DataArray itself
    base_kwargs = {**DEFAULT_XARRAY_SETTINGS, **concat_kwargs, "data_vars": "all"}

    # Rename duplicate dimensions, then concatenate
    new_dataarrays = [_rename_to_uniq_dimensions(da) for da in dataarrays]
    concatenated_dataarray = xr.concat(new_dataarrays, dim=concat_dim, **base_kwargs)

    # reconstruct the old list of dimensions and coordinates with repeated dims
    old_dims = [dim.split("___", 1)[-1] for dim in concatenated_dataarray.dims]
    old_coords = {
        old_dim: concatenated_dataarray.coords[new_dim].rename({new_dim: old_dim})
        for old_dim, new_dim in zip(old_dims, concatenated_dataarray.dims, strict=False)
        if new_dim in concatenated_dataarray.coords
    }

    # construct DataArray again with original dimension schema
    dataarray_back = xr.DataArray(
        concatenated_dataarray.to_numpy(),
        dims=old_dims,
        coords=old_coords,
        name=concatenated_dataarray.name,
        attrs=concatenated_dataarray.attrs,
    )
    # preserve encoding for storage in NetCDF4
    dataarray_back.encoding = dataarrays[0].encoding

    return dataarray_back


def _concat_datasets(datasets: list[xr.DataSet], concat_dim: str, concat_kwargs: dict):
    """Concatenate datasets, handling variables with duplicate dimensions specially."""

    # Build base kwargs
    base_kwargs = {**DEFAULT_XARRAY_SETTINGS, **concat_kwargs}

    # Find all variables with duplicate dimensions using first dataset
    duplicate_variables = _find_variables_with_duplicate_dimensions(datasets[0])

    if not duplicate_variables:
        return xr.concat(datasets, dim=concat_dim, **base_kwargs)

    # Concatenate datarrays first without duplicate dimensions
    clean_datasets = [dataset.drop_vars(duplicate_variables) for dataset in datasets]
    concatenated_dataset = xr.concat(clean_datasets, dim=concat_dim, **base_kwargs)

    # Process each duplicate variable separately
    for variable in duplicate_variables:
        dataarray = _concat_with_duplicate_dims(
            [dataset[variable] for dataset in datasets], concat_dim, concat_kwargs
        )
        concatenated_dataset = concatenated_dataset.assign({variable: dataarray})

    return concatenated_dataset


def _create_concat_function(concat_method: str, concat_dim: str, concat_kwargs: dict) -> Callable:
    """Create concatenation function after validating method and dimension requirements."""
    validate_concat_method_and_dim(concat_method, concat_dim)

    # Build base kwargs
    base_kwargs = {**DEFAULT_XARRAY_SETTINGS, **concat_kwargs}

    # Create appropriate function
    if concat_method == "xarray-concat":
        return partial(_concat_datasets, concat_dim=concat_dim, concat_kwargs=concat_kwargs)
    else:  # concat_method == "xarray-combine"
        return partial(xr.combine_by_coords, **base_kwargs)


def _load_and_sort_datatrees(
    input_files: list[str], sorting_variable: str | None, logger: Logger
) -> list[xr.DataTree]:
    """Load datatrees from files, validate consistency, and return sorted list."""
    loaded_data = []
    expected_keys = None

    for i, filepath in enumerate(input_files):
        logger.info("Processing file %03d/%03d <%s>", i + 1, len(input_files), filepath)

        # Load datatree with standard options
        datatree = xr.open_datatree(filepath, **DATATREE_OPEN_OPTIONS)

        # Validate consistency and get sort value
        expected_keys = _check_dataset_consistency(datatree, expected_keys, i + 1, filepath)
        sort_value = _get_sort_value(datatree, sorting_variable, filepath, i, logger)

        loaded_data.append((sort_value, datatree))

    # Sort by values and return datatrees
    return [datatree for _, datatree in sorted(loaded_data)]


def _check_dataset_consistency(
    datatree: xr.DataTree, expected_keys: set | None, file_num: int, filepath: str
) -> set:
    """Check that dataset keys are consistent across files."""
    current_keys = set(datatree.to_dict().keys())

    if expected_keys is None:
        return current_keys

    if current_keys != expected_keys:
        diff = current_keys ^ expected_keys
        raise KeyError(
            f"File {file_num} ({filepath}) has mismatched dataset nodes. "
            f"Expected: {sorted(expected_keys)}, got: {sorted(current_keys)}, "
            f"differences: {sorted(diff)}"
        )
    return expected_keys


def _get_sort_value(
    datatree: xr.DataTree, sorting_variable: str | None, filepath: str, index: int, logger: Logger
) -> float | int:
    """Extract sorting value from datatree or return file index."""
    if not sorting_variable:
        return index

    try:
        return datatree[sorting_variable].values.flatten()[0]
    except Exception as err:
        logger.error(
            "Cannot extract sorting value from '%s' in %s: %s", sorting_variable, filepath, err
        )
        raise


def _concatenate_datatrees(datatree_list: list[xr.DataTree], concat_func: Callable) -> xr.DataTree:
    """Concatenate datatrees using a pre-configured concatenation function (e.g., partial(xr.concat, dim='time'))"""
    if not datatree_list:
        raise ValueError("Cannot concatenate empty list of datatrees")

    # Convert to dictionaries and get dataset keys (should be consistent across all trees)
    tree_dicts = [tree.to_dict() for tree in datatree_list]
    dataset_keys = set(tree_dicts[0].keys())

    # Concatenate each dataset separately
    concatenated_datasets = {}
    for key in dataset_keys:
        # Extract the same dataset from each tree
        datasets_to_concat = [tree_dict[key] for tree_dict in tree_dicts]
        # Concatenate this dataset across all trees
        concatenated_datasets[key] = concat_func(datasets_to_concat)

    return xr.DataTree.from_dict(concatenated_datasets)


def _finalize_output(
    output_tree: xr.DataTree, output_file: str, history_to_append: str | None
) -> None:
    """Add history and save the output tree."""
    if history_to_append is not None:
        output_tree.attrs["history_json"] = history_to_append
    output_tree.to_netcdf(output_file)
