"""A simple CLI wrapper around the main concatenation process."""

import json
import logging
import sys
from argparse import ArgumentParser

import netCDF4 as nc

from concatenator.attribute_handling import construct_history, retrieve_history
from concatenator.file_ops import validate_input_path, validate_output_path
from concatenator.stitchee import stitchee


def parse_args(args: list) -> tuple[list[str], str, str, bool, str, dict, bool]:
    """
    Parse args for this script.

    Returns
    -------
    tuple
    """
    parser = ArgumentParser(
        prog="stitchee", description="Run the along-existing-dimension concatenator."
    )

    # Required arguments
    req_grp = parser.add_argument_group(title="Required")
    req_grp.add_argument(
        "input",
        metavar="path/directory or path list",
        nargs="+",
        help="Files to be concatenated, specified via a "
        "(1) single directory containing the files to be concatenated, "
        "(2) single text file containing linebreak-separated paths of the files to be concatenated, "
        "or (3) multiple filepaths of the files to be concatenated.",
    )
    req_grp.add_argument(
        "-o",
        "--output_path",
        required=True,
        help="The output filename for the merged output.",
    )

    # Optional arguments
    parser.add_argument(
        "--copy_input_files",
        action="store_true",
        help="By default, input files are not copied. "
        "This option copies the input files into a temporary directory to avoid modification "
        "of input files. This is useful for testing, but uses more disk space.  "
        "By specifying this argument, no copying is performed.",
    )
    parser.add_argument(
        "--keep_tmp_files",
        action="store_true",
        help="Prevents removal, after successful execution, of "
        "(1) the flattened concatenated file and "
        "(2) the input directory copy  if created by '--make_dir_copy'.",
    )
    parser.add_argument(
        "--concat_method",
        choices=["xarray-concat", "xarray-combine"],
        default="xarray-concat",
        help="Whether to use the xarray concat method or the combine-by-coords method.",
    )
    parser.add_argument(
        "--concat_dim",
        help="Dimension to concatenate along, if possible.  "
        "This is required if using the 'xarray-concat' method",
    )
    parser.add_argument(
        "--xarray_arg_compat",
        help="'compat' argument passed to xarray.concat() or xarray.combine_by_coords().",
    )
    parser.add_argument(
        "--xarray_arg_combine_attrs",
        help="'combine_attrs' argument passed to xarray.concat() or xarray.combine_by_coords().",
    )
    parser.add_argument(
        "--xarray_arg_join",
        help="'join' argument passed to xarray.concat() or xarray.combine_by_coords().",
    )
    parser.add_argument(
        "-O", "--overwrite", action="store_true", help="Overwrite output file if it already exists."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output to stdout; useful for debugging",
        action="store_true",
    )

    parsed = parser.parse_args(args)

    if parsed.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Validate the input and output paths
    output_path = validate_output_path(parsed.output_path, parsed.overwrite)
    input_files = validate_input_path(parsed.input)

    print(f"CONCAT METHOD === {parsed.concat_method}")
    print(f"CONCAT DIM === {parsed.concat_dim}")
    if parsed.concat_method == "xarray-concat":
        if not parsed.concat_dim:
            raise ValueError(
                "If using the xarray-concat method, then 'concat_dim' must be specified."
            )
    elif parsed.concat_method == "xarray-combine":
        if parsed.concat_dim:
            raise ValueError(
                "If using the xarray-combine method, then 'concat_dim' cannot be specified."
            )

    # Gather the concatenation arguments that will be passed to xarray.
    concat_kwargs = {}
    if parsed.xarray_arg_compat:
        concat_kwargs["compat"] = parsed.xarray_arg_compat
    if parsed.xarray_arg_combine_attrs:
        concat_kwargs["combine_attrs"] = parsed.xarray_arg_combine_attrs
    if parsed.xarray_arg_join:
        concat_kwargs["join"] = parsed.xarray_arg_join

    return (
        input_files,
        output_path,
        parsed.concat_dim,
        bool(parsed.keep_tmp_files),
        parsed.concat_method,
        concat_kwargs,
        parsed.copy_input_files,
    )


def run_stitchee(args: list) -> None:
    """
    Parse arguments and run subsetter on the specified input file
    """
    (
        input_files,
        output_path,
        concat_dim,
        keep_tmp_files,
        concat_method,
        concat_kwargs,
        copy_input_files,
    ) = parse_args(args)
    num_inputs = len(input_files)

    history_json: list[dict] = []
    for file_count, file in enumerate(input_files):
        with nc.Dataset(file, "r") as dataset:
            history_json.extend(retrieve_history(dataset))

    history_json.append(construct_history(input_files, input_files))

    new_history_json = json.dumps(history_json, default=str)

    logging.info("Executing stitchee concatenation on %d files...", num_inputs)
    stitchee(
        input_files,
        output_path,
        write_tmp_flat_concatenated=keep_tmp_files,
        keep_tmp_files=keep_tmp_files,
        concat_method=concat_method,
        concat_dim=concat_dim,
        concat_kwargs=concat_kwargs,
        history_to_append=new_history_json,
        copy_input_files=copy_input_files,
    )
    logging.info("STITCHEE complete. Result in %s", output_path)


def main() -> None:
    """Entry point to the script"""
    logging.basicConfig(
        stream=sys.stdout,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    run_stitchee(sys.argv[1:])


if __name__ == "__main__":
    main()
