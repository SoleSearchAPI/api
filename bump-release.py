import subprocess
import re


def update_version(version_type):
    filepath = "src/api/main.py"
    with open(filepath, "r") as f:
        lines = f.readlines()

    version_line_index = None
    version_pattern = re.compile(
        r'^__version__\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']\s*$'
    )
    for i, line in enumerate(lines):
        if version_pattern.match(line):
            version_line_index = i
            break

    if version_line_index is None:
        raise ValueError("Version line not found.")

    current_version = version_pattern.match(lines[version_line_index])
    major_version, minor_version, patch_version = current_version.groups()
    if version_type == "major":
        major_version = str(int(major_version) + 1)
        minor_version = "0"
        patch_version = "0"
    elif version_type == "minor":
        minor_version = str(int(minor_version) + 1)
        patch_version = "0"
    elif version_type == "patch":
        patch_version = str(int(patch_version) + 1)
    else:
        raise ValueError("Invalid version type. Please use major, minor, or patch.")

    new_version = f"{major_version}.{minor_version}.{patch_version}"
    lines[version_line_index] = f'__version__ = "{new_version}"\n'

    with open(filepath, "w") as file:
        file.writelines(lines)

    return f"v{new_version}"


# passes the command line argument to the function
if __name__ == "__main__":
    import sys

    new_version = update_version(sys.argv[1])
    message = input(f"Version updated to {new_version}. Enter commit message: \n")
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", message.strip()])
    subprocess.run(["git", "push"])
    subprocess.run(["git", "tag", "-a", new_version, "-m", message.strip()])
    subprocess.run(["git", "push", "origin", new_version])
