import json
import os
import re
from typing import List

PROFILE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\-\s_\.]+$")


def get_profile_path(profile_name: str) -> str:
    return os.path.join("profiles", profile_name)


def get_profile_names() -> List[str]:
    names = []

    for name in os.listdir("profiles"):
        path = get_profile_path(name)
        f_profile = os.path.join(path, "profile.json")

        if (
            PROFILE_NAME_PATTERN.match(name)
            and os.path.isdir(path)
            and os.path.isfile(f_profile)
        ):
            names.append(name)

    return names


def check_profile_name(name: str) -> bool:
    if PROFILE_NAME_PATTERN.match(name):
        return True

    return False


def has_profile(name: str):
    return name in get_profile_names()


def generate_profile(game_root: str, game_exe: str, mods_dir: str):
    profile = {
        "root": game_root,
        "game": game_exe,
        "mods": mods_dir,
    }

    return json.dumps(profile, separators=(", ", ": "), indent=4)
