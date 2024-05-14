"""Convenience variables used across the package."""

from dataclasses import dataclass
from importlib.metadata import version


@dataclass
class Options:
    """Options for concatenator."""

    group_delim = "__"
    coord_delim = "  "


__version__ = version("stitchee")

global _options
_options = Options()


def __getattr__(name):  # type: ignore
    """Module-level getattr to handle accessing `concatenator.options`.

    Other unhandled attributes raise as `AttributeError` as expected.
    """
    if name == "__options__":
        return _options
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __setattr__(name, value):  # type: ignore
    """Module-level setattr to handle setting of `concatenator.options`.

    Other unhandled attributes raise as `AttributeError` as expected.
    """
    if name == "group_delim":
        _options.group_delim = value
    elif name == "coord_delim":
        _options.coord_delim = value
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
