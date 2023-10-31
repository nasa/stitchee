from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pystac
from harmony.adapter import BaseHarmonyAdapter
from harmony.util import bbox_to_geometry
from pystac import Item
from pystac.item import Asset

from concatenator.harmony.download_worker import multi_core_download
from concatenator.harmony.util import (
    _get_netcdf_urls,
    _get_output_bounding_box,
    _get_output_date_range,
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

    def process_catalog(self, catalog: pystac.Catalog):
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
            filename = f"{collection}_merged.nc4"

            with TemporaryDirectory() as temp_dir:
                self.logger.info("Starting granule downloads")
                input_files = multi_core_download(
                    netcdf_urls, temp_dir, self.message.accessToken, self.config
                )
                self.logger.info("Finished granule downloads")

                output_path = str(Path(temp_dir).joinpath(filename).resolve())

                # # --- Run STITCHEE ---
                stitchee(
                    input_files,
                    output_path,
                    write_tmp_flat_concatenated=False,
                    keep_tmp_files=False,
                    concat_dim="mirror_step",  # This is currently set only for TEMPO
                    logger=self.logger,
                )
                staged_url = self._stage(output_path, filename, "application/x-netcdf4")

            # -- Output to STAC catalog --
            result.clear_items()
            properties = dict(
                start_datetime=datetimes["start_datetime"], end_datetime=datetimes["end_datetime"]
            )

            item = Item(
                str(uuid4()), bbox_to_geometry(bounding_box), bounding_box, None, properties
            )
            asset = Asset(
                staged_url, title=filename, media_type="application/x-netcdf4", roles=["data"]
            )
            item.add_asset("data", asset)
            result.add_item(item)

            self.logger.info("STAC catalog creation complete.")

            return result

        except Exception as service_exception:
            self.logger.error(service_exception, exc_info=1)
            raise service_exception
