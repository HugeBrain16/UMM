@echo off
nuitka -j 4 --msvc=latest --onefile --include-plugin-directory=lib,menus -o UniversalModManager.exe main.py