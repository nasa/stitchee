"""A simple CLI wrapper around the main concatenation process."""
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from concatenator.bumblebee import bumblebee


def parse_args(args: list) -> tuple:
    """
    Parse args for this script.

    Returns
    -------
    tuple
    """
    parser = ArgumentParser(
        prog='bumblebee',
        description='Run the along-existing-dimension concatenator.')
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

    parsed = parser.parse_args(args)

    if parsed.verbose:
        logging.basicConfig(level=logging.DEBUG)

    return parsed.data_dir, parsed.output_path

def run_bumblebee(args: list) -> None:
    """
    Parse arguments and run subsetter on the specified input file
    """
    data_dir, output_path = parse_args(args)

    input_files = [str(f) for f in Path(data_dir).resolve().iterdir()]
    num_inputs = len(input_files)

    logging.info('Executing bumblebee concatenation on %d files...', num_inputs)
    bumblebee(input_files, output_path)
    logging.info('BUMBLEBEE complete. Result in %s', output_path)


def main() -> None:
    """Entry point to the script"""
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    run_bumblebee(sys.argv[1:])


if __name__ == '__main__':
    main()
