"""A Harmony CLI wrapper around the concatenate-batcher"""

from argparse import ArgumentParser

import harmony_service_lib

from stitchee.harmony.service_adapter import StitcheeAdapter as HarmonyAdapter


def main(config: harmony_service_lib.util.Config = None) -> None:
    """Parse command line arguments and invoke the service to respond to them.

    Parameters
    ----------
    config : harmony.util.Config
        harmony.util.Config is injectable for tests

    Returns
    -------
    None
    """
    parser = ArgumentParser(
        prog="Stitchee", description="Run the STITCH by Extending a dimEnsion service"
    )
    harmony_service_lib.setup_cli(parser)
    args = parser.parse_args()
    if harmony_service_lib.is_harmony_cli(args):
        harmony_service_lib.run_cli(parser, args, HarmonyAdapter, cfg=config)
    else:
        parser.error("Only --harmony CLIs are supported")


if __name__ == "__main__":
    main()
