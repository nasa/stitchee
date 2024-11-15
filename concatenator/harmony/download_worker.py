"""A utility for downloading multiple granules simultaneously"""

import queue
import re
from copy import deepcopy
from multiprocessing import Manager, Process
from os import cpu_count
from pathlib import Path
from urllib.parse import urlparse

from harmony_service_lib.logging import build_logger
from harmony_service_lib.util import download


def multi_core_download(
    urls: list,
    destination_dir: str,
    access_token: str,
    cfg: dict,
    process_count: int | None = None,
) -> list[Path]:
    """
    A method which automagically scales downloads to the number of CPU
    cores. For further explaination, see documentation on "multi-track
    drifting"

    Parameters
    ----------
    urls : list
        list of urls to download
    destination_dir : str
        output path for downloaded files
    access_token : str
        access token as provided in Harmony input
    cfg : dict
        Harmony configuration information
    process_count : int, optional
        Number of worker processes to run (expected >= 1)

    Returns
    -------
    list of downloaded files as pathlib.Path objects
    """

    if process_count is None:
        process_count = cpu_count()
    if process_count is None:
        raise RuntimeError("cannot determine number of cpus")

    with Manager() as manager:
        url_queue = manager.Queue(len(urls))
        path_list = manager.list()

        for url in urls:
            url_queue.put(url)

        # Spawn worker processes
        processes = []
        for _ in range(process_count):
            download_process = Process(
                target=_download_worker,
                args=(url_queue, path_list, destination_dir, access_token, cfg),
            )
            processes.append(download_process)
            download_process.start()

        # Ensure worker processes exit successfully
        for process in processes:
            process.join()
            if process.exitcode != 0:
                raise RuntimeError(f"Download failed - exit code: {process.exitcode}")

            process.close()

        path_list = deepcopy(path_list)  # ensure GC can cleanup multiprocessing

    return [Path(path) for path in path_list]


def _download_worker(
    url_queue: queue.Queue,
    path_list: list,
    destination_dir: str,
    access_token: str,
    cfg: dict,
) -> None:
    """
    A method to be executed in a separate process which processes the url_queue
    and places paths to completed downloads into the path_list. Downloads are
    handled by harmony.util.download

    Parameters
    ----------
    url_queue : queue.Queue
        URLs to process - should be filled from start and only decreases
    path_list : list
        paths to completed file downloads
    destination_dir : str
        output path for downloaded files
    access_token : str
        access token as provided in Harmony input
    cfg : dict
        Harmony configuration information
    """

    logger = build_logger(cfg)

    while not url_queue.empty():
        try:
            url = url_queue.get_nowait()
        except queue.Empty:
            break

        path = Path(
            download(url, destination_dir, logger=logger, access_token=access_token, cfg=cfg)
        )
        filename_match = re.match(r".*\/(.+\..+)", urlparse(url).path)

        if filename_match is not None:
            filename = filename_match.group(1)
            dest_path = path.parent.joinpath(filename)
            path = path.rename(dest_path)
        else:
            logger.warning("Origin filename could not be ascertained - %s", url)

        path_list.append(str(path))
