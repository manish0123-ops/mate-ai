
import os
import re
import json
import winreg
from pathlib import Path
from functools import lru_cache

CUSTOM_FILE = Path(__file__).with_name("custom_apps.json")


def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.casefold())


def load_custom_apps():
    try:
        with open(CUSTOM_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


@lru_cache(maxsize=1)
def find_shortcuts():
    shortcuts = []

    for variable in ("APPDATA", "PROGRAMDATA"):
        root = os.environ.get(variable)

        if root:
            folder = (
                Path(root)
                / "Microsoft/Windows/Start Menu/Programs"
            )

            if folder.is_dir():
                try:
                    for path in folder.rglob("*.lnk"):
                        shortcuts.append((path.stem, path))
                except OSError:
                    pass

    return shortcuts


def list_apps():
    names = {name for name, _ in find_shortcuts()}
    names.update(load_custom_apps().keys())

    return sorted(names, key=str.casefold)


def find_registered_executable(app_name):
    """Look for an executable registered in Windows App Paths."""
    target = normalize(app_name)
    if not target.endswith("exe"):
        target += "exe"

    registry_path = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
    )

    locations = [
        (winreg.HKEY_CURRENT_USER, 0),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
    ]

    for hive, view in locations:
        try:
            with winreg.OpenKey(
                hive,
                registry_path,
                0,
                winreg.KEY_READ | view,
            ) as root:
                count = winreg.QueryInfoKey(root)[0]

                for index in range(count):
                    try:
                        entry = winreg.EnumKey(root, index)

                        if normalize(entry) != target:
                            continue

                        with winreg.OpenKey(root, entry) as key:
                            executable, _ = winreg.QueryValueEx(key, "")

                        executable = os.path.expandvars(
                            executable.strip().strip('"')
                        )

                        if Path(executable).is_file():
                            return Path(executable)

                    except OSError:
                        continue
        except OSError:
            continue

    return None


def launch_path(path):
    path = Path(os.path.expandvars(str(path).strip().strip('"')))

    if not path.is_file():
        return f"Path does not exist: {path}"

    try:
        os.startfile(str(path))
        return f"Opening {path.name}."
    except OSError as error:
        return f"Could not open application: {error}"


def open_app(app_name):
    requested = app_name.strip()
    key = normalize(requested)

    if not key:
        return "Please provide an application name."

    built_in = {
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
    }

    for name, command in built_in.items():
        if key == normalize(name):
            try:
                import subprocess
                subprocess.Popen(command)
                return f"Opening {name}."
            except OSError as error:
                return f"Could not open {name}: {error}"

    # 1. Exact or partial Start Menu shortcut match
    shortcuts = find_shortcuts()

    matches = [
        (name, path)
        for name, path in shortcuts
        if normalize(name) == key
    ]

    if not matches:
        matches = [
            (name, path)
            for name, path in shortcuts
            if key in normalize(name)
        ]

    if len(matches) == 1:
        try:
            os.startfile(str(matches[0][1]))
            return f"Opening {matches[0][0]}."
        except OSError as error:
            return f"Could not open {matches[0][0]}: {error}"

    if len(matches) > 1:
        choices = ", ".join(name for name, _ in matches[:8])
        return f"Multiple matches: {choices}. Please be more specific."

    # 2. Custom executable paths
    custom_apps = load_custom_apps()

    custom_matches = [
        (name, path)
        for name, path in custom_apps.items()
        if normalize(name) == key
    ]

    if len(custom_matches) == 1:
        return launch_path(custom_matches[0][1])

    # 3. Windows registered executable fallback
    executable = find_registered_executable(requested)

    if executable:
        return launch_path(executable)

    return (
        f"Could not find a launch method for '{requested}'. "
        "Check the app's Start Menu shortcut or add its executable "
        "path to custom_apps.json."
    )

