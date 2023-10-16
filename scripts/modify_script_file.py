import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("BASE_DIR--->", BASE_DIR)
sys.path.insert(0, BASE_DIR)

from utils import public_func


def modify_spec_file() -> None:
    print("Modify main.spec...")
    project_path = BASE_DIR
    project_path = "\\\\".join(project_path.split("\\")) + "\\\\"
    print("project_path--->", project_path)
    file_path = os.path.join(BASE_DIR, "main.spec")
    new_str = ""
    with open(file_path, encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("PROJECT_PATH"):
                line = f'PROJECT_PATH = "{project_path}"\n'

            new_str += line

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_str)


def modify_bat_file() -> None:
    print("Modify bat files...")
    bat_file_64 = "build_windows_x64.bat"
    bat_file_32 = "build_windows_x86.bat"
    product_version = public_func.generate_product_version()

    def _modify_bat_file(file_path: str) -> None:
        new_str = ""
        with open(file_path, encoding="utf-8") as f:
            for line in f.readlines():
                if line.startswith("set PRODUCT_VERSION"):
                    line = f"set PRODUCT_VERSION=v{product_version}\n"

                new_str += line

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_str)

    _modify_bat_file(bat_file_64)
    _modify_bat_file(bat_file_32)


def modify_nsis_file() -> None:
    print("Modify nsis files...")
    nsis_file_64 = os.path.join("toolkits", "build_windows_x64.nsi")
    nsis_file_32 = os.path.join("toolkits", "build_windows_x86.nsi")
    product_version = public_func.generate_product_version()
    project_path = BASE_DIR

    def _modify_nsis_file(file_path: str) -> None:
        new_str = ""
        with open(file_path, encoding="gbk") as f:
            for line in f.readlines():
                if line.startswith("!define PRODUCT_VERSION"):
                    line = f'!define PRODUCT_VERSION "v{product_version}"\n'
                elif line.startswith("!define PROJECT_DIR"):
                    line = f'!define PROJECT_DIR "{project_path}"\n'

                new_str += line

        with open(file_path, "w", encoding="gbk") as f:
            f.write(new_str)

    _modify_nsis_file(nsis_file_64)
    _modify_nsis_file(nsis_file_32)


def modify_shell_file() -> None:
    print("Modify build_mac.sh...")
    product_version = public_func.generate_product_version()
    file_path = "build_mac.sh"
    new_str = ""
    with open(file_path, encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("PRODUCT_VERSION"):
                line = f'PRODUCT_VERSION = "v{product_version}"\n'

            new_str += line

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_str)


if __name__ == "__main__":
    system = public_func.get_system()
    if system == "Windows":
        modify_spec_file()
        modify_bat_file()
        modify_nsis_file()
    elif system == "Darwin":
        modify_shell_file()
    else:
        print(f"Unsupported system: {system}")
        sys.exit(1)
