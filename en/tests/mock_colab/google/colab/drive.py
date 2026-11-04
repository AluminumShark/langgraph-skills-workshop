"""A fake google.colab.drive: creates a local folder to stand in for Google Drive."""

from pathlib import Path


def mount(mountpoint: str, force_remount: bool = False) -> None:
    (Path(mountpoint) / "MyDrive").mkdir(parents=True, exist_ok=True)
    print(f"(mock) Mounted at {mountpoint}")
