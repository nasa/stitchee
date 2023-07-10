"""For running local tests without installing package."""
import logging
import sys

from concatenator.run_bumblebee import run_bumblebee


def main() -> None:
    """Entry point to the script"""
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    run_bumblebee(sys.argv[1:])


if __name__ == '__main__':
    main()
