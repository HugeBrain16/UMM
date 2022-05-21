import json
import os
import shutil
import subprocess
import sys

from lib import libinput, libmeta, libprofile


def _print_profile_list():
    [
        print(f"{idx + 1}). {name}")
        for idx, name in enumerate(libprofile.get_profile_names())
    ]


def main():
    libinput.clear()
    print("Universal Mod Manager v" + libmeta.__version__ + "\n")
    print("[PROFILES]")
    _print_profile_list()
    print("N). New profile")
    print("D). Delete profile")
    print("Q/E). Quit")
    opt = libinput.get("> ", main).lower()

    if not opt.isdigit():
        if opt == "q" or opt == "e":
            return sys.exit(0)
        elif opt == "n":
            libinput.clear()
            return new()
        elif opt == "d":
            libinput.clear()
            return delete()
        else:
            libinput.clear()
            print("Invalid option!")
            return main()
    else:
        opt = int(opt) - 1
        profiles = libprofile.get_profile_names()

        try:
            name = profiles[opt]
            profile = json.load(
                open(os.path.join("profiles", name, "profile.json"), "r")
            )
        except IndexError:
            libinput.clear()
            print("Invalid profile!")
            return main()

        tempdir = os.path.join("profiles", name, ".temp")

        if os.path.isdir(tempdir):
            shutil.rmtree(tempdir)
        os.makedirs(tempdir)
        os.makedirs(os.path.join(tempdir, "togame"))
        os.makedirs(os.path.join(tempdir, "backup"))

        print("Copying mods...")
        for mod in os.listdir(os.path.join("profiles", name, "mods")):
            print(f"[MOD] Copying {mod!r}...")
            for root, dirs, files in os.walk(
                os.path.join("profiles", name, "mods", mod)
            ):
                copyto = root.replace(
                    os.path.join("profiles", name, "mods", mod),
                    os.path.join(tempdir, "togame"),
                )
                for file in files:
                    src = os.path.join(root, file)
                    dest = os.path.join(copyto, file)
                    print(f"[MOD] Copying file {src!r} to {dest!r}...")

                    if os.path.isfile(dest):
                        print(f"[WARN] Overwriting file {dest!r} with {src!r}...")

                    dest_parent = os.path.split(dest)[0]
                    if not os.path.isdir(dest_parent):
                        os.makedirs(dest_parent)

                    shutil.copy2(src, dest)

        print("Copying mods to gamefile...")
        for root, dirs, files in os.walk(os.path.join(tempdir, "togame")):
            copyto = root.replace(os.path.join(tempdir, "togame"), profile["mods"])
            backupto = root.replace(
                os.path.join(tempdir, "togame"), os.path.join(tempdir, "backup")
            )

            for file in files:
                src = os.path.join(root, file)
                dest = os.path.join(copyto, file)
                print(f"[MOD] Copying file {src!r} to {dest!r}...")

                if os.path.isfile(dest):
                    shutil.copy2(dest, os.path.join(backupto, file))
                    print(f"[WARN] Overwriting file {dest!r} with {src!r}...")

                dest_parent = os.path.split(dest)[0]
                if not os.path.isdir(dest_parent):
                    os.makedirs(dest_parent)

                shutil.copy2(src, dest)

        game = subprocess.Popen(
            profile["game"],
            creationflags=subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP,
            cwd=profile["root"],
        )

        # poll process until its closed
        while True:
            try:
                poll = game.poll()

                if poll is not None:
                    break
            except (EOFError, KeyboardInterrupt):
                print("[WARN] Close from the game!")

        print("Copying backup to gamefile...")
        for root, dirs, files in os.walk(os.path.join(tempdir, "togame")):
            copyto = root.replace(os.path.join(tempdir, "backup"), profile["mods"])
            for file in files:
                src = os.path.join(tempdir, "togame", file)
                dest = os.path.join(profile["mods"], file)
                backup = os.path.join(tempdir, "backup", file)

                if os.path.isfile(src) and not os.path.isfile(backup):
                    if os.path.isfile(dest):
                        print(f"[MOD] Removing {dest!r}...")
                        os.remove(dest)
                elif os.path.isfile(src) and os.path.isfile(backup):
                    print(f"[MOD] Restoring backuped file {backup!r} to {dest!r}...")
                    shutil.copy2(backup, dest)

        if os.path.isdir(tempdir):
            shutil.rmtree(tempdir)
        return main()


def delete():
    print("Select profile to delete:")
    _print_profile_list()
    opt = libinput.get("> ", main).strip()

    if not opt.isdigit():
        libinput.clear()
        print("Input must be digits!")
        return delete()

    opt = int(opt) - 1
    profiles = libprofile.get_profile_names()
    try:
        shutil.rmtree(os.path.join("profiles", profiles[opt]))
    except IndexError:
        libinput.clear()
        print("Invalid profile!")
        return delete()

    print("Profile deleted!")
    return main()


def new():
    name = libinput.get("Enter profile name: ", main).strip()

    if not libprofile.check_profile_name(name):
        libinput.clear()
        print("Invalid profile name!")
        return new()
    if libprofile.has_profile(name):
        libinput.clear()
        print("Profile already exists: " + name)
        return new()

    def get_game_root():
        game_root = libinput.get("Enter game root directory: ", new).strip()

        if not os.path.isdir(game_root):
            libinput.clear()
            print("Directory doesn't exist!")
            return get_game_root()

        return game_root

    def get_game_exe(game_root):
        game_exe = libinput.get("Enter game executable: ", new).strip()

        if not os.path.isfile(os.path.join(game_root, game_exe)):
            libinput.clear()
            print("File doesn't exist!")
            return get_game_exe(game_root)

        return game_exe

    def get_mods_dir(game_root):
        mods_dir = libinput.get(
            "Enter mods directory (leave empty to set it to the game root): ",
            allow_empty=True,
        ).strip()

        if not os.path.isdir(os.path.join(game_root, mods_dir)):
            libinput.clear()
            print("Directory doesn't exist!")
            return get_mods_dir(game_root)

        return mods_dir

    game_root = get_game_root()
    game_exe = get_game_exe(game_root)
    mods_dir = get_mods_dir(game_root)

    # update path to the absolute path
    game_root = os.path.abspath(game_root)
    game_exe = os.path.abspath(os.path.join(game_root, game_exe))
    mods_dir = (
        os.path.abspath(os.path.join(game_root, mods_dir)) if mods_dir else game_root
    )

    print("Creating profile directory...")
    profile_path = os.path.join("profiles", name)
    os.makedirs(profile_path)
    subdirs = ["mods"]
    for subdir in subdirs:
        os.makedirs(os.path.join(profile_path, subdir))

    print("Generating profile.json file...")
    profile = libprofile.generate_profile(game_root, game_exe, mods_dir)
    f_profile = open(os.path.join(profile_path, "profile.json"), "w")
    f_profile.write(profile)
    f_profile.close()

    print("Profile created!")
    return main()
