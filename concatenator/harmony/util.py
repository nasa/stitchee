"""Misc utility functions"""
from datetime import datetime

from pystac import Asset, Item

VALID_EXTENSIONS = (".nc4", ".nc")
VALID_MEDIA_TYPES = ["application/x-netcdf", "application/x-netcdf4"]


def _is_netcdf_asset(asset: Asset) -> bool:
    """Check that a `pystac.Asset` is a valid NetCDF-4 granule. This can be
    ascertained via either the media type or by checking the extension of
    granule itself if that media type is absent.

    """
    return asset.media_type in VALID_MEDIA_TYPES or (
        asset.media_type is None and asset.href.lower().endswith(VALID_EXTENSIONS)
    )


def _get_item_url(item: Item) -> str | None:
    """Check the `pystac.Item` for the first asset with the `data` role and a
    valid input format. If there are no matching assets, return None

    """
    return next(
        (
            asset.href
            for asset in item.assets.values()
            if "data" in (asset.roles or []) and _is_netcdf_asset(asset)
        ),
        None,
    )


def _get_netcdf_urls(items: list[Item]) -> list[str]:
    """Iterate through a list of `pystac.Item` instances, from the input
    `pystac.Catalog`. Extract the `pystac.Asset.href` for the first asset
    of each item that has a role of "data". If there are any items that do
    not have a data asset, then raise an exception.

    """
    catalog_urls = [_get_item_url(item) for item in items]

    if None in catalog_urls:
        raise RuntimeError("Some input granules do not have NetCDF-4 assets.")

    return catalog_urls  # type: ignore[return-value]


def _get_output_bounding_box(input_items: list[Item]) -> list[float]:
    """Create a bounding box that is the maximum combined extent of all input
    `pystac.Item` bounding box extents.

    """
    bounding_box = input_items[0].bbox

    for item in input_items:
        bounding_box[0] = min(bounding_box[0], item.bbox[0])
        bounding_box[1] = min(bounding_box[1], item.bbox[1])
        bounding_box[2] = max(bounding_box[2], item.bbox[2])
        bounding_box[3] = max(bounding_box[3], item.bbox[3])

    return bounding_box


def _get_output_date_range(input_items: list[Item]) -> dict[str, str]:
    """Create a dictionary of start and end datetime, which encompasses the
    full temporal range of all input `pystac.Item` instances. This output
    dictionary will be used for the `properties` of the output Zarr store
    `pystac.Item`.

    """
    start_datetime, end_datetime = _get_item_date_range(input_items[0])

    for item in input_items:
        new_start_datetime, new_end_datetime = _get_item_date_range(item)
        start_datetime = min(start_datetime, new_start_datetime)
        end_datetime = max(end_datetime, new_end_datetime)

    return {"start_datetime": start_datetime.isoformat(), "end_datetime": end_datetime.isoformat()}


def _get_item_date_range(item: Item) -> tuple[datetime, datetime]:
    """A helper function to retrieve the temporal range from a `pystac.Item`
    instance. If the `pystac.Item.datetime` property exists, there is a
    single datetime associated with the granule, otherwise there will be a
    start and end time contained within the `pystac.Item` metadata.

    """
    if item.datetime is None:
        start_datetime = item.common_metadata.start_datetime
        end_datetime = item.common_metadata.end_datetime
    else:
        start_datetime = item.datetime
        end_datetime = item.datetime

    return start_datetime, end_datetime
