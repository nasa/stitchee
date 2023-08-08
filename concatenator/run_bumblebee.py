"""A simple CLI wrapper around the main concatenation process."""
import logging
import os
import shutil
import sys
import uuid
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple, Union

from concatenator.bumblebee import bumblebee
from concatenator.file_ops import add_label_to_path


def parse_args(args: list) -> Tuple[list[str], str, bool, Union[str, None]]:
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
        '--keep_tmp_files',
        action='store_true',
        help="Prevents removal, after successful execution, of "
             "(1) the flattened concatenated file and "
             "(2) the input directory copy  if created by '--make_dir_copy'.")
    parser.add_argument(
        '-O', '--overwrite',
        action='store_true',
        help='Overwrite output file if it already exists.')
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose output to stdout; useful for debugging',
        action='store_true'
    )

    parsed = parser.parse_args(args)

    if parsed.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # The output file path is validated.
    output_path = Path(parsed.output_path).resolve()
    if output_path.is_file():  # the file already exists
        if parsed.overwrite:
            os.remove(output_path)
        else:
            raise FileExistsError(f"File already exists at <{output_path}>. Run again with option '-O' to overwrite.")

    # The input directory is validated.
    data_dir = Path(parsed.data_dir).resolve()
    if not data_dir.is_dir():
        raise TypeError("'data_dir' must be an existing directory.")

    # If requested, make a copy of the input directory
    temporary_dir_to_remove = None
    if parsed.make_dir_copy:
        new_data_dir = add_label_to_path(str(data_dir), label=f"_copy{str(uuid.uuid4())}")
        shutil.copytree(data_dir, new_data_dir)

        print('Created temporary directory: %s', new_data_dir)
        data_dir = Path(new_data_dir).resolve()

        temporary_dir_to_remove = str(data_dir)

    # Get list of files (ignoring hidden files) in directory.
    input_files = [str(f) for f in data_dir.iterdir() if not f.name.startswith(".")]

    return input_files, str(output_path), bool(parsed.keep_tmp_files), temporary_dir_to_remove

def run_bumblebee(args: list) -> None:
    """
    Parse arguments and run subsetter on the specified input file
    """
    input_files, output_path, keep_tmp_files, temporary_dir_to_remove = parse_args(args)
    num_inputs = len(input_files)

    logging.info('Executing bumblebee concatenation on %d files...', num_inputs)
    bumblebee(input_files, output_path, keep_tmp_files=keep_tmp_files)
    logging.info('BUMBLEBEE complete. Result in %s', output_path)

    if not keep_tmp_files and temporary_dir_to_remove:
        shutil.rmtree(temporary_dir_to_remove)


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
