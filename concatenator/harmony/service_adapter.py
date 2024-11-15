import json
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from uuid import uuid4

import netCDF4 as nc
import pystac
from harmony_service_lib.adapter import BaseHarmonyAdapter
from harmony_service_lib.util import bbox_to_geometry, stage
from pystac import Item
from pystac.item import Asset

from concatenator.attribute_handling import construct_history, retrieve_history
from concatenator.harmony.download_worker import multi_core_download
from concatenator.harmony.util import (
    _get_netcdf_urls,
    _get_output_bounding_box,
    _get_output_date_range,
    sizeof_fmt,
)
from concatenator.stitchee import stitchee


class StitcheeAdapter(BaseHarmonyAdapter):
    """
    A harmony-service-lib wrapper around the concatenate-batcher module.
    This wrapper does not support Harmony calls that do not have STAC catalogs
    as support for this behavior is being depreciated in harmony-service-lib
    """

    def __init__(self, message, catalog=None, config=None):
        """
        Constructs the adapter

        Parameters
        ----------
        message : harmony.Message
            The Harmony input which needs acting upon
        catalog : pystac.Catalog
            A STAC catalog containing the files on which to act
        config : harmony.util.Config
            The configuration values for this runtime environment.
        """
        super().__init__(message, catalog=catalog, config=config)

    def invoke(self):
        """
        Primary entrypoint into the service wrapper. Overrides BaseHarmonyAdapter.invoke
        """
        if not self.catalog:
            # Message-only support is being depreciated in Harmony, so we should expect to
            # only see requests with catalogs when invoked with a newer Harmony instance
            # https://github.com/nasa/harmony-service-lib-py/blob/21bcfbda17caf626fb14d2ac4f8673be9726b549/harmony/adapter.py#L71
            raise RuntimeError("Invoking Batchee without a STAC catalog is not supported")

        return self.message, self.process_catalog(self.catalog)

    def process_catalog(self, catalog: pystac.Catalog) -> pystac.Catalog:
        """Converts a list of STAC catalogs into a list of lists of STAC catalogs."""
        self.logger.info("process_catalog() started.")
        try:
            result = catalog.clone()
            result.id = str(uuid4())
            result.clear_children()

            # Get all the items from the catalog, including from child or linked catalogs
            items = list(self.get_all_catalog_items(catalog))

            self.logger.info(f"length of items==={len(items)}.")

            # Quick return if catalog contains no items
            if len(items) == 0:
                return result

            # # --- Get granule filepaths (urls) ---
            netcdf_urls: list[str] = _get_netcdf_urls(items)
            self.logger.info(f"netcdf_urls==={netcdf_urls}.")

            # -- Process metadata --
            bounding_box: list | None = _get_output_bounding_box(items)
            datetimes = _get_output_date_range(items)

            # Items did not have a bbox; valid under spec
            if bounding_box and len(bounding_box) == 0:
                bounding_box = None

            # -- Perform merging --
            collection = self._get_item_source(items[0]).collection

            number_of_granules = len(netcdf_urls)
            first_url_name = Path(netcdf_urls[0]).stem
            filename = f"{collection}_batch_of_{number_of_granules}_starting_from_{first_url_name}_stitched.nc4"
            self.logger.info(f"Merged filename will be === {filename}.")

            with TemporaryDirectory() as temp_dir:
                self.logger.info("Starting granule downloads")
                input_files = multi_core_download(
                    netcdf_urls, temp_dir, self.message.accessToken, self.config
                )
                self.logger.info("Finished granule downloads.")

                history_json: list[dict] = []
                for file_count, file in enumerate(input_files):
                    file_size = sizeof_fmt(file.stat().st_size)
                    self.logger.info(f"File {file_count} is size <{file_size}>. Path={file}")

                    with nc.Dataset(file, "r") as dataset:
                        history_json.extend(retrieve_history(dataset))

                history_json.append(construct_history(input_files, netcdf_urls))

                new_history_json = json.dumps(history_json, default=str)

                self.logger.info("Running Stitchee..")
                output_path = str(Path(temp_dir).joinpath(filename).resolve())

                # # --- Run STITCHEE ---
                stitchee(
                    [str(f) for f in input_files],
                    output_path,
                    write_tmp_flat_concatenated=False,
                    keep_tmp_files=False,
                    concat_dim="mirror_step",  # This is currently set only for TEMPO
                    sorting_variable="geolocation/time",  # This is currently set only for TEMPO
                    history_to_append=new_history_json,
                    logger=self.logger,
                )
                self.logger.info("Stitchee completed.")
                staged_url = self._stage(output_path, filename, "application/x-netcdf4")
                self.logger.info("Staging completed.")

            # -- Output to STAC catalog --
            result.clear_items()
            properties = dict(
                start_datetime=datetimes["start_datetime"],
                end_datetime=datetimes["end_datetime"],
            )

            item = Item(
                str(uuid4()),
                bbox_to_geometry(bounding_box),
                bounding_box,
                None,
                properties,
            )
            asset = Asset(
                staged_url,
                title=filename,
                media_type="application/x-netcdf4",
                roles=["data"],
            )
            item.add_asset("data", asset)
            result.add_item(item)

            self.logger.info("STAC catalog creation complete.")

            return result

        except Exception as service_exception:
            self.logger.error(service_exception, exc_info=1)
            raise service_exception

    def _stage(self, local_filename: str, remote_filename: str, mime: str) -> str:
        """
        Stages a local file to either to S3 (utilizing harmony.util.stage) or to
        the local filesystem by performing a file copy. Staging location is
        determined by message.stagingLocation or the --harmony-data-location
        CLI argument override

        Parameters
        ----------
        local_filename : string
            A path and filename to the local file that should be staged
        remote_filename : string
            The basename to give to the remote file
        mime : string
            The mime type to apply to the staged file for use when it is served, e.g. "application/x-netcdf4"

        Returns
        -------
        url : string
            A URL to the staged file
        """
        url_components = urlsplit(self.message.stagingLocation)
        scheme = url_components.scheme

        if scheme == "file":
            dest_path = Path(url_components.path).joinpath(remote_filename)
            self.logger.info("Staging to local filesystem: '%s'", str(dest_path))

            copyfile(local_filename, dest_path)
            return dest_path.as_uri()

        return stage(
            local_filename,
            remote_filename,
            mime,
            logger=self.logger,
            location=self.message.stagingLocation,
            cfg=self.config,
        )
