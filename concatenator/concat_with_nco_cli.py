"""A simple CLI wrapper around the main NCO concatenation function"""
import logging
import shutil
import sys

from concatenator.concat_with_nco import concat_netcdf_files
from concatenator.run_bumblebee import parse_args


def run_nco_concat(args: list) -> None:
    """
    Parse arguments and run subsetter on the specified input file
    """
    input_files, output_path, keep_tmp_files, temporary_dir_to_remove = parse_args(args)
    num_inputs = len(input_files)

    logging.info('Executing NCO concatenation on %d files...', num_inputs)
    concat_netcdf_files(input_files, output_path)
    logging.info('NCO concatenation complete. Result in %s', output_path)

    if not keep_tmp_files and temporary_dir_to_remove:
        shutil.rmtree(temporary_dir_to_remove)


def main() -> None:
    """Entry point to the script"""
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    run_nco_concat(sys.argv[1:])


if __name__ == '__main__':
    main()
