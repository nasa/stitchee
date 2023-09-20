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
usage: stitchee [-h] -o output_path [--concat_dim concat_dim] [--make_dir_copy] [--keep_tmp_files] [-O] [-v]
                path/directory or path list [path/directory or path list ...]

Run the along-existing-dimension concatenator.

options:
  -h, --help            show this help message and exit
  --concat_dim concat_dim
                        Dimension to concatenate along, if possible.
  --make_dir_copy       Make a duplicate of the input directory to avoid modification of input files. This is useful for testing, but
                        uses more disk space.
  --keep_tmp_files      Prevents removal, after successful execution, of (1) the flattened concatenated file and (2) the input
                        directory copy if created by '--make_dir_copy'.
  -O, --overwrite       Overwrite output file if it already exists.
  -v, --verbose         Enable verbose output to stdout; useful for debugging

Required:
  path/directory or path list
                        Files to be concatenated, specified via a (1) single directory containing the files to be concatenated, (2)
                        single text file containing linebreak-separated paths of the files to be concatenated, or (3) multiple
                        filepaths of the files to be concatenated.
  -o output_path, --output_path output_path
                        The output filename for the merged output.
```

For example:

```shell
poetry run stitchee /path/to/netcdf/directory/ /path/to/output.nc
```

## Roadmap
Next major milestone(s):
- Conduct extensive tests
- Incorporate this service into Harmony as a Docker image.
