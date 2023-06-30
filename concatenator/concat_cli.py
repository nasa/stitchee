"""A simple CLI wrapper around the main merge function"""

import logging
from argparse import ArgumentParser
from pathlib import Path

from concatenator.concat_with_nco import concat_netcdf_files


def main():
    """Main CLI entrypoint"""

    parser = ArgumentParser(
        prog='recon',
        description='Simple CLI wrapper around the granule record concatenator module.')
    parser.add_argument(
        'data_dir',
        help='The directory containing the files to be merged.')
    parser.add_argument(
        'output_path',
        help='The output filename for the merged output.')
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose output to stdout; useful for debugging',
        action='store_true'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    input_files = list(Path(args.data_dir).resolve().iterdir())
    concat_netcdf_files(input_files, args.output_path)


if __name__ == '__main__':
    main()
