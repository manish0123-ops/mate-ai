
import os
import winreg
from pathlib import Path


def find_installed_apps():
    apps = {}

    # 1. Scan Windows installed-app registry entries
    registry_locations = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            winreg.KEY_WOW64_64KEY,
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            winreg.KEY_WOW64_32KEY,
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            0,
        ),
    ]

    for hive, subkey, view_flag in registry_locations:
        try:
            with winreg.OpenKey(
                hive, subkey, 0, winreg.KEY_READ | view_flag
            ) as root:
                count = winreg.QueryInfoKey(root)[0]

                for index in range(count):
                    try:
                        child_name = winreg.EnumKey(root, index)

                        with winreg.OpenKey(root, child_name) as child:
                            name, _ = winreg.QueryValueEx(
                                child, "DisplayName"
                            )

                            if not isinstance(name, str) or not name.strip():
                                continue

                            try:
                                publisher, _ = winreg.QueryValueEx(
                                    child, "Publisher"
                                )
                            except OSError:
                                publisher = ""

                            apps[name.strip()] = {
                                "name": name.strip(),
                                "publisher": publisher,
                                "source": "Installed-app registry",
                            }

                    except OSError:
                        continue
        except OSError:
            continue

    # 2. Scan Start Menu shortcuts (including many Store app shortcuts)
    appdata = os.environ.get("APPDATA")
    programdata = os.environ.get("PROGRAMDATA")

    start_menu_folders = []

    if appdata:
        start_menu_folders.append(
            Path(appdata) / "Microsoft/Windows/Start Menu/Programs"
        )

    if programdata:
        start_menu_folders.append(
            Path(programdata) / "Microsoft/Windows/Start Menu/Programs"
        )

    for folder in start_menu_folders:
        if not folder.is_dir():
            continue

        try:
            for shortcut in folder.rglob("*.lnk"):
                name = shortcut.stem.strip()

                if name:
                    apps.setdefault(
                        name,
                        {
                            "name": name,
                            "publisher": "",
                            "source": "Start Menu shortcut",
                        },
                    )
        except OSError:
            continue

    return sorted(
        apps.values(),
        key=lambda app: app["name"].casefold(),
    )


def main():
    apps = find_installed_apps()

    print(f"\nMATE found {len(apps)} application entries:\n")

    for number, app in enumerate(apps, start=1):
        publisher = app["publisher"]
        extra = f" — {publisher}" if publisher else ""
        print(f"{number:3}. {app['name']}{extra}")

    # Save the results locally for MATE to use later
    output_file = Path(__file__).with_name("installed_apps.txt")

    with open(output_file, "w", encoding="utf-8") as file:
        for app in apps:
            file.write(app["name"] + "\n")

    print(f"\nSaved the list to: {output_file}")


if __name__ == "__main__":
    main()
