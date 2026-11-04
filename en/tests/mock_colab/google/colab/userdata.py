"""A fake google.colab.userdata: reads "Secrets" from environment variables."""

import os


class SecretNotFoundError(Exception):
    pass


def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    raise SecretNotFoundError(key)
