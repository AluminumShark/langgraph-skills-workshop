"""A fake google.colab.files: "downloading" just prints the file name."""

from pathlib import Path


def download(filename: str) -> None:
    size = Path(filename).stat().st_size
    print(f"(mock) Downloading {filename} ({size} bytes)")
