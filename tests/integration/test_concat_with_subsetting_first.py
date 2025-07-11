import datetime as dt

from harmony import BBox, Client, Collection, Request

from stitchee.concatenate import concatenate


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
        extend=False,
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
    output_path = concatenate(
        file_names,
        output_file=str(
            (temp_output_dir / "output_harmony_subsetting_to_stitchee_test.nc").resolve()
        ),
        concat_dim="mirror_step",
        concat_method="xarray-concat",
    )

    assert output_path
