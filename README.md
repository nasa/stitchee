[<img src="https://github.com/danielfromearth/stitchee/assets/114174502/58052dfa-b6e1-49e5-96e5-4cb1e8d14c32" width="250"/>](stitchee_9_hex)

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

## Roadmap
Next major milestone(s):
- Conduct extensive tests
- Incorporate this service into Harmony as a Docker image.
