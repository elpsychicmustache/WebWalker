from pathlib import Path

from directory_asset import DirectoryAsset

def main() -> None:
    project_root = get_parent_path()
    input_file = project_root / "data" / "input.txt"
    output_file = project_root / "data" / "output.txt"

    running_directory_list = set()  # list of all directories (to prevent recursion/duplicates)

    with open(input_file, "r") as file:
        directories = file.read().strip()

    main_directory_asset = instantiate_directory_object("/", directories, running_directory_list)
    running_directory_list.update(main_directory_asset.children)

    main_directory_asset.print_asset_list()
    main_directory_asset.populate_child_directories()
    main_directory_asset.print_asset_list()

def get_parent_path() -> "PosixPath":
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    return project_root


def instantiate_directory_object(parent_directory, directory_list, running_directory_list) -> DirectoryAsset:
    directory_asset = DirectoryAsset(parent_directory, 0)
    directory_asset.populate_directories(directory_list, running_directory_list)
    return directory_asset


main()
