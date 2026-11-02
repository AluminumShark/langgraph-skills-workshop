"""假的 google.colab.userdata：從環境變數讀「密鑰」。"""

import os


class SecretNotFoundError(Exception):
    pass


def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    raise SecretNotFoundError(key)
