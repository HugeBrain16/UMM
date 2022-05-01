import os

clear = lambda: os.system("cls" if os.name == "nt" else "clear")


def _get(prompt: str, on_interupt=None) -> str:
    x = ""

    try:
        x = input(prompt)
    except (EOFError, KeyboardInterrupt) as exception:
        if on_interupt:
            return on_interupt()
        else:
            raise exception

    return x


def get(prompt: str, on_interupt=None, allow_empty: bool = False):
    x = _get(prompt, on_interupt)

    while not x.strip() and not allow_empty:
        x = _get(prompt, on_interupt)

    return x
