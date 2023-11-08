"""A simple CLI wrapper around the main concatenation process."""
import logging
import os
import shutil
import sys
import uuid
from argparse import ArgumentParser
from pathlib import Path

from concatenator.file_ops import add_label_to_path
from concatenator.stitchee import stitchee


def parse_args(args: list) -> tuple[list[str], str, str, bool, str | None]:
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
        metavar="output_path",
        required=True,
        help="The output filename for the merged output.",
    )

    # Optional arguments
    parser.add_argument(
        "--concat_dim",
        metavar="concat_dim",
        nargs=1,
        help="Dimension to concatenate along, if possible.",
    )
    parser.add_argument(
        "--no_input_file_copies",
        action="store_true",
        help="By default, input files are copied into a temporary directory to avoid modification "
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

    # The output file path is validated.
    output_path = Path(parsed.output_path).resolve()
    if output_path.is_file():  # the file already exists
        if parsed.overwrite:
            os.remove(output_path)
        else:
            raise FileExistsError(
                f"File already exists at <{output_path}>. Run again with option '-O' to overwrite."
            )

    # The input directory or file is validated.
    print(f"parsed_input === {parsed.input}")
    if len(parsed.input) > 1:
        input_files = parsed.input
    elif len(parsed.input) == 1:
        directory_or_path = Path(parsed.input[0]).resolve()
        if directory_or_path.is_dir():
            input_files = _get_list_of_filepaths_from_dir(directory_or_path)
        elif directory_or_path.is_file():
            input_files = _get_list_of_filepaths_from_file(directory_or_path)
        else:
            raise TypeError(
                "if one path is provided for 'data_dir_or_file_or_filepaths', "
                "then it must be an existing directory or file."
            )
    else:
        raise TypeError("input argument must be one path/directory or a list of paths.")

    # If requested, make a temporary directory with copies of the original input files
    temporary_dir_to_remove = None
    if not parsed.no_input_file_copies:
        new_data_dir = Path(
            add_label_to_path(str(output_path.parent / "temp_copy"), label=str(uuid.uuid4()))
        ).resolve()
        os.makedirs(new_data_dir, exist_ok=True)
        print("Created temporary directory: %s", str(new_data_dir))

        new_input_files = []
        for file in input_files:
            new_path = new_data_dir / Path(file).name
            shutil.copyfile(file, new_path)
            new_input_files.append(str(new_path))

        input_files = new_input_files
        print("Copied files to temporary directory: %s", new_data_dir)
        temporary_dir_to_remove = str(new_data_dir)

    return (
        input_files,
        str(output_path),
        parsed.concat_dim[0],
        bool(parsed.keep_tmp_files),
        temporary_dir_to_remove,
    )


def _get_list_of_filepaths_from_file(file_with_paths: Path):
    # Each path listed in the specified file is resolved using pathlib for validation.
    paths_list = []
    with open(file_with_paths, encoding="utf-8") as file:
        while line := file.readline():
            paths_list.append(str(Path(line.rstrip()).resolve()))

    return paths_list


def _get_list_of_filepaths_from_dir(data_dir: Path):
    # Get list of files (ignoring hidden files) in directory.
    input_files = [str(f) for f in data_dir.iterdir() if not f.name.startswith(".")]
    return input_files


def run_stitchee(args: list) -> None:
    """
    Parse arguments and run subsetter on the specified input file
    """
    input_files, output_path, concat_dim, keep_tmp_files, temporary_dir_to_remove = parse_args(args)
    num_inputs = len(input_files)

    logging.info("Executing stitchee concatenation on %d files...", num_inputs)
    stitchee(
        input_files,
        output_path,
        write_tmp_flat_concatenated=keep_tmp_files,
        keep_tmp_files=keep_tmp_files,
        concat_dim=concat_dim,
    )
    logging.info("STITCHEE complete. Result in %s", output_path)

    if not keep_tmp_files and temporary_dir_to_remove:
        shutil.rmtree(temporary_dir_to_remove)


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
