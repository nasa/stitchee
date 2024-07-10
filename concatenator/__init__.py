"""Convenience variables used across the package."""

from dataclasses import dataclass
from importlib.metadata import version


@dataclass
class Options:
    """Options for concatenator."""

    group_delim = "__"
    coord_delim = "  "


__version__ = version("stitchee")

_options = Options()


def __getattr__(name):  # type: ignore
    """Module-level getattr to handle accessing `concatenator.options`.

    Other unhandled attributes raise as `AttributeError` as expected.
    """
    global _options

    if name == "group_delim":
        return _options.group_delim
    if name == "coord_delim":
        return _options.coord_delim
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
