from pathlib import Path

from directory_asset import DirectoryAsset
from directory_navigator import DirectoryNavigator

def main() -> None:
    project_root = get_parent_path()
    input_file = project_root / "data" / "input.txt"
    output_file = project_root / "data" / "output.txt"

    # TODO: eventually, this will need to be changed to checking if a directory is already populated
    #   for now, this will just be the entry point.
    with open(input_file, "r") as file:
        directories = file.read().strip()

    main_directory_asset = instantiate_directory_object("/", directories)

    navigator = DirectoryNavigator(main_directory_asset)

    main_directory_asset.populate_child_directories()
    main_directory_asset.print_asset_list()

def get_parent_path() -> "PosixPath":
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    return project_root


def instantiate_directory_object(parent_directory, directory_list) -> DirectoryAsset:
    directory_asset = DirectoryAsset(parent_directory, 2)
    directory_asset.populate_directories(directory_list)
    return directory_asset


main()
