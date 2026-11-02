"""假的 google.colab.drive：在本機建一個資料夾當作雲端硬碟。"""

from pathlib import Path


def mount(mountpoint: str, force_remount: bool = False) -> None:
    (Path(mountpoint) / "MyDrive").mkdir(parents=True, exist_ok=True)
    print(f"(mock) Mounted at {mountpoint}")
