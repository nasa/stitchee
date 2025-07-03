"""A simple CLI wrapper around the main concatenation process."""

import argparse
import logging
import sys
from argparse import ArgumentParser

from stitchee.concatenate import (
    SUPPORTED_CONCAT_METHODS,
    concatenate,
    validate_concat_method_and_dim,
)
from stitchee.file_ops import validate_input_path, validate_output_path
from stitchee.history_handling import collect_history

# Configure module-level logger
logger = logging.getLogger(__name__)

# Module constants
DEFAULT_CONCAT_METHOD = "xarray-concat"


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments for the stitchee concatenation tool."""
    parser = ArgumentParser(
        prog="stitchee",
        description="Concatenate netCDF files along an existing dimension.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  stitchee file1.nc file2.nc -o output.nc --concat_dim time
  stitchee /path/to/files/ -o output.nc --concat_method xarray-combine
  stitchee filelist.txt -o output.nc --concat_dim time --sorting_variable time
        """,
    )

    # Required arguments
    req_grp = parser.add_argument_group(title="Required Arguments")
    req_grp.add_argument(
        "input",
        metavar="INPUT",
        nargs="+",
        help="Input specification: multiple file paths, directory path, "
        "text file with file list, or single file to copy",
    )
    req_grp.add_argument(
        "-o",
        "--output_path",
        required=True,
        metavar="PATH",
        help="Output file path for concatenated result",
    )

    # Concatenation options
    concat_grp = parser.add_argument_group("Concatenation Options")
    concat_grp.add_argument(
        "--concat_method",
        choices=SUPPORTED_CONCAT_METHODS,
        default=DEFAULT_CONCAT_METHOD,
        help="Concatenation method (default: %(default)s)",
    )
    concat_grp.add_argument(
        "--concat_dim",
        metavar="DIM",
        help="Dimension to concatenate along (required for xarray-concat)",
    )
    concat_grp.add_argument(
        "--sorting_variable",
        metavar="VAR",
        help="Name of a variable to use for sorting datasets before concatenation (e.g., 'time')",
    )

    # xarray arguments
    xarray_grp = parser.add_argument_group("xarray Arguments")
    for arg, meta, help_text in [
        ("--xarray_arg_compat", "COMPAT", "'compat' argument for xarray functions"),
        ("--xarray_arg_combine_attrs", "ATTRS", "'combine_attrs' argument for xarray functions"),
        ("--xarray_arg_join", "JOIN", "'join' argument for xarray functions"),
    ]:
        xarray_grp.add_argument(arg, metavar=meta, help=help_text)

    # Other options
    parser.add_argument(
        "-O",
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it exists",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output to stdout; useful for debugging",
    )

    return parser.parse_args(args)


def _validate_args(
    parsed: argparse.Namespace,
) -> tuple[list[str], str, str, str, dict]:
    """Validate parsed arguments and return processed values."""
    if parsed.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("stitchee").setLevel(logging.DEBUG)

    # Validate paths and concatenation requirements
    try:
        input_files = validate_input_path(parsed.input)
        output_path = validate_output_path(parsed.output_path, parsed.overwrite)
        validate_concat_method_and_dim(parsed.concat_method, parsed.concat_dim)
    except Exception as e:
        logger.error("Validation failed: %s", e)
        raise

    # Build concatenation kwargs to be passed to xarray.
    concat_kwargs = {}
    if parsed.xarray_arg_compat:
        concat_kwargs["compat"] = parsed.xarray_arg_compat
    if parsed.xarray_arg_combine_attrs:
        concat_kwargs["combine_attrs"] = parsed.xarray_arg_combine_attrs
    if parsed.xarray_arg_join:
        concat_kwargs["join"] = parsed.xarray_arg_join

    # Log configuration
    logger.info("Concatenation method: %s", parsed.concat_method)
    logger.info("Concatenation dimension: %s", parsed.concat_dim or "N/A")
    logger.info("Input files found: %d", len(input_files))

    return input_files, output_path, parsed.concat_dim, parsed.concat_method, concat_kwargs


def run_concatenate(args: list[str]) -> None:
    """Parse arguments and run concatenation on specified input files."""
    try:
        # Parse and validate arguments
        parsed_args = parse_args(args)
        input_files, output_path, concat_dim, concat_method, concat_kwargs = _validate_args(
            parsed_args
        )

        logger.info("Collecting history from %d input files...", len(input_files))
        history_json = collect_history(input_files)

        logger.info("Starting concatenation...")
        result_path = concatenate(
            input_files,
            output_path,
            concat_method=concat_method,
            concat_dim=concat_dim,
            concat_kwargs=concat_kwargs,
            sorting_variable=parsed_args.sorting_variable,
            history_to_append=history_json,
            overwrite_output_file=parsed_args.overwrite,
        )

        # Log results
        if result_path:
            logger.info("Concatenation completed successfully. Result in %s", result_path)
        else:
            logger.info("No output generated (likely no valid input files)")

    except KeyboardInterrupt:
        logger.error("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Concatenation failed: %s", e)
        sys.exit(1)


def main() -> None:
    """Entry point for the stitchee command line tool."""
    logging.basicConfig(
        stream=sys.stdout,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    run_concatenate(sys.argv[1:])


if __name__ == "__main__":
    main()
