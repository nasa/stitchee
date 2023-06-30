from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

import netCDF4 as nc
import pytest

from concatenator.concat_with_nco import concat_netcdf_files


def is_file_empty(parent_group):
    """
    Function to test if a all variable size in a dataset is 0
    """

    for var in parent_group.variables.values():
        if var.size != 0:
            return False
    for child_group in parent_group.groups.values():
        return is_file_empty(child_group)
    return True


@pytest.mark.usefixtures("pass_options")
class TestConcat(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.__test_path = Path(__file__).parent.resolve()
        cls.__test_data_path = cls.__test_path.joinpath('data')
        cls.__output_path = Path(mkdtemp(prefix='tmp-', dir=cls.__test_data_path))

    @classmethod
    def tearDownClass(cls):
        if not cls.KEEP_TMP:  # pylint: disable=no-member
            rmtree(cls.__output_path)

    def run_verification(self, data_dir, output_name, process_count=None):
        output_path = str(self.__output_path.joinpath(output_name))
        data_path = self.__test_data_path.joinpath(data_dir)
        input_files = [str(x) for x in data_path.iterdir()]

        dim_for_record_dim = 'mirror_step'
        concat_netcdf_files(input_files, output_path,
                            dim_for_record_dim=dim_for_record_dim,
                            decompress_datasets=True)

        merged_dataset = nc.Dataset(output_path)

        # Verify that the length of the record dimension in the concatenated file equals
        #   the sum of the lengths across the input files
        length_sum = 0
        for file in input_files:
            length_sum += len(nc.Dataset(file).variables[dim_for_record_dim])
        assert length_sum == len(merged_dataset.variables[dim_for_record_dim])

    def test_tempo_no2_concat(self):
        self.run_verification('tempo_no2', 'tempo_no2_concat.nc')

    def test_tempo_hcho_concat(self):
        self.run_verification('tempo_hcho', 'tempo_hcho_concat.nc')
