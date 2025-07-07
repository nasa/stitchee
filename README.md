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
and it is designed as both a standalone utility and for use as a service in [Harmony](https://harmony.earthdata.nasa.gov/).

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

For example:

```shell
poetry run stitchee /path/to/files/directory -o output.nc --concat_method xarray-combine
```

Command line options:
```shell
$ poetry run stitchee --help
usage: stitchee [-h] -o PATH [--concat_method {xarray-concat,xarray-combine}] [--concat_dim DIM] [--sorting_variable VAR] [--xarray_arg_compat COMPAT]
                [--xarray_arg_combine_attrs ATTRS] [--xarray_arg_join JOIN] [-O] [-v]
                INPUT [INPUT ...]

Concatenate netCDF files along existing dimensions.

options:
  -h, --help            show this help message and exit
  -O, --overwrite       Overwrite output file if it exists
  -v, --verbose         Enable verbose output to stdout; useful for debugging

Required Arguments:
  INPUT                 Input specification: multiple file paths, directory path, text file with file list, or single file to copy
  -o PATH, --output_path PATH
                        Output file path for concatenated result

Concatenation Options:
  --concat_method {xarray-concat,xarray-combine}
                        Concatenation method (default: xarray-concat)
  --concat_dim DIM      Dimension to concatenate along (required for xarray-concat)
  --sorting_variable VAR
                        Name of a variable to use for sorting datasets before concatenation (e.g., 'time')

xarray Arguments:
  --xarray_arg_compat COMPAT
                        'compat' argument passed to xarray concatenation function
  --xarray_arg_combine_attrs ATTRS
                        'combine_attrs' argument passed to xarray concatenation function
  --xarray_arg_join JOIN
                        'join' argument passed to xarray concatenation function

Examples:
  stitchee file1.nc file2.nc -o output.nc --concat_dim time
  stitchee /path/to/files/directory -o output.nc --concat_method xarray-combine
  stitchee filelist.txt -o output.nc --concat_dim time --sorting_variable time
```

---
This package is NASA Software Release Authorization (SRA) # LAR-20433-1
