"""A simple CLI wrapper around the main concatenation process."""
import logging
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple

from concatenator.bumblebee import bumblebee
from concatenator.file_ops import add_label_to_path


def parse_args(args: list) -> Tuple[list[str], str]:
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
        '--make_dir_copy',
        action='store_true',
        help='Make a duplicate of the input directory to avoid modification of input files. '
             'This is useful for testing, but uses more disk space.')
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose output to stdout; useful for debugging',
        action='store_true'
    )

    parsed = parser.parse_args(args)

    if parsed.verbose:
        logging.basicConfig(level=logging.DEBUG)

    data_dir = Path(parsed.data_dir).resolve()
    if parsed.make_dir_copy:
        new_data_dir = add_label_to_path(str(data_dir), label="_copy")
        shutil.copytree(data_dir, new_data_dir)
        print('Created temporary directory: %s', new_data_dir)
        data_dir = Path(new_data_dir).resolve()

    input_files = [str(f) for f in data_dir.iterdir()]

    return input_files, parsed.output_path

def run_bumblebee(args: list) -> None:
    """
    Parse arguments and run subsetter on the specified input file
    """
    input_files, output_path = parse_args(args)
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
