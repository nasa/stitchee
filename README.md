<p align="center">
    <img alt="stitchee, a python package for concatenating netCDF data along an existing dimension"
    src="https://github.com/danielfromearth/stitchee/assets/114174502/58052dfa-b6e1-49e5-96e5-4cb1e8d14c32" width="250"
    />
</p>

<p align="center">
    <a href="https://www.repostatus.org/#active" target="_blank">
        <img src="https://www.repostatus.org/badges/latest/active.svg" alt="Project Status: Active – The project has reached a stable, usable state and is being actively developed">
    </a>
    <a href='https://stitchee.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/stitchee/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://github.com/python/black" target="_blank">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style">
    </a>
    <a href="http://mypy-lang.org/" target="_blank">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="Mypy checked">
    </a>
    <a href="https://pypi.org/project/stitchee/" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/stitchee.svg" alt="Python Versions">
    </a>
    <a href="https://pypi.org/project/stitchee" target="_blank">
        <img src="https://img.shields.io/pypi/v/stitchee?color=%2334D058label=pypi%20package" alt="Package version">
    </a>
    <a href="https://codecov.io/gh/nasa/stitchee">
     <img src="https://codecov.io/gh/nasa/stitchee/graph/badge.svg?token=WDj92iN7c4" alt="Code coverage">
    </a>
</p>

[//]: # (Using deprecated `align="center"` for the logo image and badges above, because of https://stackoverflow.com/a/62383408)

# Overview
_____

_STITCHEE_ (STITCH by Extending a dimEnsion) is used for concatenating netCDF data *along an existing dimension*,
and it is deigned as both a standalone utility and for use as a service in [Harmony](https://harmony.earthdata.nasa.gov/).

## Getting started, with poetry

1. Follow the instructions for installing `poetry` [here](https://python-poetry.org/docs/).
2. Install `stitchee`, with its dependencies, by running the following from the repository directory:

```shell
poetry install
```

## How to test `stitchee` locally

```shell
poetry run pytest tests/
```

## Usage

```shell
$ poetry run stitchee --help
usage: stitchee [-h] -o OUTPUT_PATH [--no_input_file_copies] [--keep_tmp_files] [--concat_method {xarray-concat,xarray-combine}] [--concat_dim CONCAT_DIM]
                [--xarray_arg_compat XARRAY_ARG_COMPAT] [--xarray_arg_combine_attrs XARRAY_ARG_COMBINE_ATTRS] [--xarray_arg_join XARRAY_ARG_JOIN] [-O]
                [-v]
                path/directory or path list [path/directory or path list ...]

Run the along-existing-dimension concatenator.

options:
  -h, --help            show this help message and exit
  --no_input_file_copies
                        By default, input files are copied into a temporary directory to avoid modification of input files. This is useful for testing,
                        but uses more disk space. By specifying this argument, no copying is performed.
  --keep_tmp_files      Prevents removal, after successful execution, of (1) the flattened concatenated file and (2) the input directory copy if created
                        by '--make_dir_copy'.
  --concat_method {xarray-concat,xarray-combine}
                        Whether to use the xarray concat method or the combine-by-coords method.
  --concat_dim CONCAT_DIM
                        Dimension to concatenate along, if possible. This is required if using the 'xarray-concat' method
  --xarray_arg_compat XARRAY_ARG_COMPAT
                        'compat' argument passed to xarray.concat() or xarray.combine_by_coords().
  --xarray_arg_combine_attrs XARRAY_ARG_COMBINE_ATTRS
                        'combine_attrs' argument passed to xarray.concat() or xarray.combine_by_coords().
  --xarray_arg_join XARRAY_ARG_JOIN
                        'join' argument passed to xarray.concat() or xarray.combine_by_coords().
  --group_delim GROUP_DELIM
                        Character or string to use as group delimiter
  -O, --overwrite       Overwrite output file if it already exists.
  -v, --verbose         Enable verbose output to stdout; useful for debugging

Required:
  path/directory or path list
                        Files to be concatenated, specified via a (1) single directory containing the files to be concatenated, (2) single text file
                        containing linebreak-separated paths of the files to be concatenated, or (3) multiple filepaths of the files to be concatenated.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        The output filename for the merged output.
```

For example:

```shell
poetry run stitchee /path/to/netcdf/directory/ -o /path/to/output.nc
```

---
This package is NASA Software Release Authorization (SRA) # LAR-20433-1
