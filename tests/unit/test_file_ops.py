from pathlib import Path

import pytest

from concatenator.file_ops import add_label_to_path, validate_input_path, validate_output_path

from .. import data_for_tests_dir


def test_add_label_to_path():
    this_module_dir = Path(__file__).parent

    origin_path = str((this_module_dir / "tests_file.nc").resolve())
    new_path = str((this_module_dir / "tests_file_new-suffix.nc").resolve())

    assert add_label_to_path(origin_path, label="_new-suffix") == new_path


def test_validate_bad_output_paths():
    path_to_file_that_exists = str(
        data_for_tests_dir / "unit-test-data" / "TEMPO_NO2_L2_V03_20240328T154353Z_S008G01.nc4"
    )

    with pytest.raises(FileExistsError):
        validate_output_path(path_to_file_that_exists, overwrite=False)

    with pytest.raises(TypeError):
        validate_output_path(str(data_for_tests_dir), overwrite=False)


def test_validate_bad_non_existent_input_path():
    path_to_file_that_does_not_exist = str(
        data_for_tests_dir / "unit-test-data" / "non-existent.nc4"
    )

    with pytest.raises(TypeError):
        validate_input_path([path_to_file_that_does_not_exist])

    with pytest.raises(TypeError):
        validate_input_path([])
