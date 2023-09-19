"""For running local tests without installing package."""
import logging
import sys

from concatenator.run_stitchee import run_stitchee


def main() -> None:
    """Entry point to the script"""
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    run_stitchee(sys.argv[1:])


if __name__ == '__main__':
    main()
