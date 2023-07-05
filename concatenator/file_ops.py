"""File operation functions."""
from pathlib import Path


def add_label_to_path(x: str, label="_flat_intermediate") -> str:
    """Constructs new filepath with label at end."""
    pathlib_x = Path(x)
    return str(pathlib_x.parent / f"{pathlib_x.stem}{label}{pathlib_x.suffix}")
