from pathlib import Path

from concatenator.file_ops import add_label_to_path


def test_add_label_to_path():
    this_module_dir = Path(__file__).parent

    origin_path = str((this_module_dir / "tests_file.nc").resolve())
    new_path = str((this_module_dir / "tests_file_new-suffix.nc").resolve())

    assert add_label_to_path(origin_path, label="_new-suffix") == new_path
