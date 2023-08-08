# bumblebee

Tool for concatenating netCDF data *along an existing dimension*,
which is deigned as both a standalone utility and
for use as a service in [Harmony](https://harmony.earthdata.nasa.gov/).

## Getting started, with poetry

1. Follow the instructions for installing `poetry` [here](https://python-poetry.org/docs/).
2. Install `bumblebee`, with its dependencies, by running the following from the repository directory:

```shell
poetry install
```

## How to test `bumblebee` locally

```shell
poetry run pytest tests/
```

## Usage (with poetry)

```shell
$ poetry run bumblebee --help
usage: bumblebee [-h] [--make_dir_copy] [-v] data_dir output_path

Run the along-existing-dimension concatenator.

positional arguments:
  data_dir         The directory containing the files to be merged.
  output_path      The output filename for the merged output.

options:
  -h, --help       show this help message and exit
  --make_dir_copy  Make a duplicate of the input directory to avoid modification of input files. This is useful for testing, but uses more disk space.
  -v, --verbose    Enable verbose output to stdout; useful for debugging
```

For example:

```shell
poetry run bumblebee /path/to/netcdf/directory/ /path/to/output.nc
```

## Usage (without poetry)

```shell
python entry.py --help
```

## Roadmap
Next major milestone(s):
- Conduct extensive tests
- Incorporate this service into Harmony as a Docker image.
