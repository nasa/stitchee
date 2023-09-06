"""Tests for concatenation logic."""

# pylint: disable=C0116

import shutil
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

import netCDF4 as nc  # type: ignore
import pytest

from concatenator import concat_with_nco
from concatenator.bumblebee import bumblebee


@pytest.mark.usefixtures("pass_options")
class TestConcat(TestCase):
    """Main concatenation testing class."""

    @classmethod
    def setUpClass(cls):
        cls.__test_path = Path(__file__).parent.resolve()
        cls.__test_data_path = cls.__test_path.joinpath('data')
        cls.__output_path = Path(mkdtemp(prefix='tmp-', dir=cls.__test_data_path))

    @classmethod
    def tearDownClass(cls):
        if not cls.KEEP_TMP:  # pylint: disable=no-member
            rmtree(cls.__output_path)

    def run_verification_with_bumblebee(self,
                                        data_dir,
                                        output_name,
                                        record_dim_name: str = 'mirror_step'):
        output_path = str(self.__output_path.joinpath(output_name))  # type: ignore
        data_path = self.__test_data_path.joinpath(data_dir)  # type: ignore

        input_files = []
        for filepath in data_path.iterdir():
            if Path(filepath).suffix.lower() in (".nc", ".h5", ".hdf"):
                copied_input_new_path = self.__output_path / Path(filepath).name  # type: ignore
                shutil.copyfile(filepath, copied_input_new_path)
                input_files.append(str(copied_input_new_path))

        output_path = bumblebee(files_to_concat=input_files,
                                output_file=output_path,
                                write_tmp_flat_concatenated=True,
                                keep_tmp_files=True,
                                concat_dim=record_dim_name)

        merged_dataset = nc.Dataset(output_path)

        # Verify that the length of the record dimension in the concatenated file equals
        #   the sum of the lengths across the input files
        length_sum = 0
        for file in input_files:
            length_sum += len(nc.Dataset(file).variables[record_dim_name])
        assert length_sum == len(merged_dataset.variables[record_dim_name])

    def run_verification_with_nco(self, data_dir, output_name, record_dim_name='mirror_step'):
        output_path = str(self.__output_path.joinpath(output_name))
        data_path = self.__test_data_path.joinpath(data_dir)

        input_files = []
        for filepath in data_path.iterdir():
            if Path(filepath).suffix == ".nc":
                copied_input_new_path = self.__output_path / Path(filepath).name
                shutil.copyfile(filepath, copied_input_new_path)
                input_files.append(str(copied_input_new_path))

        concat_with_nco.concat_netcdf_files(input_files, output_path,
                                            dim_for_record_dim=record_dim_name,
                                            decompress_datasets=True)

        merged_dataset = nc.Dataset(output_path)

        # Verify that the length of the record dimension in the concatenated file equals
        #   the sum of the lengths across the input files
        length_sum = 0
        for file in input_files:
            length_sum += len(nc.Dataset(file).variables[record_dim_name])
        assert length_sum == len(merged_dataset.variables[record_dim_name])

    def test_tempo_no2_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('tempo/tempo_no2_two',
                                             'tempo_no2_concat_with_bumblebee.nc')

    def test_tempo_no2_many_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('tempo/tempo_no2_many',
                                             'tempo_no2_concat_many_with_bumblebee.nc')

    def test_tempo_hcho_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('tempo/tempo_hcho_two', 'tempo_hcho_concat_with_bumblebee.nc')

    def test_tempo_hcho_many_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('tempo/tempo_hcho_many', 'tempo_hcho_concat_with_bumblebee.nc')

    def test_tempo_cld04_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('tempo/tempo_cld04', 'tempo_cld04_concat_with_bumblebee.nc')

    def test_tempo_o3prof_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('tempo/tempo_o3prof', 'tempo_o3prof_concat_with_bumblebee.nc')

    def test_icesat_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('icesat', 'icesat_concat_with_bumblebee.nc')

    def test_ceres_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('ceres-subsetter-output',
                                             'ceres_concat_with_bumblebee.nc',
                                             record_dim_name='time')

    def test_ceres_flash_concat_with_bumblebee(self):
        self.run_verification_with_bumblebee('ceres_flash-subsetter-output',
                                             'ceres_flash_concat_with_bumblebee.nc',
                                             record_dim_name='time')

    # def test_tempo_no2_concat_with_nco(self):
    #     self.run_verification_with_nco('tempo_no2', 'tempo_no2_concat_with_nco.nc')
    #
    # def test_tempo_hcho_concat_with_nco(self):
    #     self.run_verification_with_nco('tempo_hcho', 'tempo_hcho_concat_with_nco.nc')
