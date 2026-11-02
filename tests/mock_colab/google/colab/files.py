"""假的 google.colab.files：下載只印出檔名。"""

from pathlib import Path


def download(filename: str) -> None:
    size = Path(filename).stat().st_size
    print(f"(mock) 下載 {filename}（{size} bytes）")
