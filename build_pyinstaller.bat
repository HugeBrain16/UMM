@echo off
pyinstaller --strip --console --onefile -n UniversalModManager --collect-submodules lib --collect-submodules menus main.py
