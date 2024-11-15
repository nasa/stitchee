import datetime as dt

from harmony import BBox, Client, Collection, Request

from concatenator.stitchee import stitchee


def test_concat_with_subsetting_first(temp_output_dir):
    """Subsets 4 granules from the TEMPO NO2 collection, and then concatenates them."""
    harmony_client = Client()

    # "Nitrogen Dioxide total column"
    request = Request(
        collection=Collection(id="C2930725014-LARC_CLOUD"),
        temporal={
            "start": dt.datetime(2024, 5, 13, 11, 0, 0),
            "stop": dt.datetime(2024, 5, 13, 20, 0, 0),
        },
        spatial=BBox(-130, 30, -115, 35),
        concatenate=False,
    )
    if not request.is_valid():
        raise RuntimeError

    # Submit and wait for job to complete.
    job_id = harmony_client.submit(request)
    print(f"Job ID: {job_id}")
    harmony_client.wait_for_processing(job_id, show_progress=False)

    # Download the result files.
    futures = harmony_client.download_all(job_id, directory=str(temp_output_dir))
    file_names = [f.result() for f in futures]
    print(f"File names: {file_names}")

    # Try concatenating the resulting files
    output_path = stitchee(
        file_names,
        output_file=str(
            (temp_output_dir / "output_harmony_subsetting_to_stitchee_test.nc").resolve()
            #         ),
            #         concat_dim="mirror_step",
            #         concat_method="xarray-concat",
            #         write_tmp_flat_concatenated=True,
            #         keep_tmp_files=True,
            #     )
            #
            #     assert output_path
            #
            # C1262899916-LARC_CLOUD
            #
            # G1269044803-LARC_CLOUD
            # G1269044708-LARC_CLOUD
            # G1269044681-LARC_CLOUD
            # G1269044688-LARC_CLOUD
            # G1269044514-LARC_CLOUD
            # G1269044741-LARC_CLOUD
            # G1269044710-LARC_CLOUD
            # G1269044439-LARC_CLOUD
            # G1269044715-LARC_CLOUD
            # G1269044815-LARC_CLOUD
            # G1269044726-LARC_CLOUD
            # G1269044787-LARC_CLOUD
            # G1269044827-LARC_CLOUD
            # G1269044658-LARC_CLOUD
            # G1269044679-LARC_CLOUD
            # G1269044727-LARC_CLOUD
            # subset=lat(32.56485%3A42.82943)&
            # subset=lon(-135.7248%3A-52.76692)&
            # subset=time(%222024-08-02T00%3A00%3A00.000Z%22%3A%222024-08-02T10%3A39%3A37.000Z%22)&
            # concatenate=true&skipPreview=true
            #
            # def test_concat_with_subsetting_first(temp_output_dir):
            #     """Subsets 4 granules from the TEMPO NO2 collection, and then concatenates them."""
            #     harmony_client = Client()
            #
            #     # "Nitrogen Dioxide total column"
            #     request = Request(
            #         collection=Collection(id="C2930725014-LARC_CLOUD"),
            #         temporal={
            #             "start": dt.datetime(2024, 5, 13, 11, 0, 0),
            #             "stop": dt.datetime(2024, 5, 13, 20, 0, 0),
            #         },
            #         spatial=BBox(-130, 30, -115, 35),
            #         concatenate=False,
            #     )
            #     if not request.is_valid():
            #         raise RuntimeError
            #
            #     # Submit and wait for job to complete.
            #     job_id = harmony_client.submit(request)
            #     print(f"Job ID: {job_id}")
            #     harmony_client.wait_for_processing(job_id, show_progress=False)
            #
            #     # Download the result files.
            #     futures = harmony_client.download_all(job_id, directory=str(temp_output_dir))
            #     file_names = [f.result() for f in futures]
            #     print(f"File names: {file_names}")
            #
            #     # Try concatenating the resulting files
            #     output_path = stitchee(
            #         file_names,
            #         output_file=str(
            #             (temp_output_dir / "output_harmony_subsetting_to_stitchee_test.nc").resolve()
        ),
        concat_dim="mirror_step",
        concat_method="xarray-concat",
        write_tmp_flat_concatenated=True,
        keep_tmp_files=True,
    )

    assert output_path
