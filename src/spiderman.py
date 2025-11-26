import argparse
import textwrap

from pathlib import Path

from directory_asset import DirectoryAsset
from directory_navigator import DirectoryNavigator

# TODO: Implement curses.


def main() -> None:
    """Running this starts the program.

    It grabs the input file, which should be '../data/input.txt' if default option for --input_file is used.
    Using this file, it creates the root directory, and then populates children directories from the input file.

    It then creates the DirectoryNavigator object, which then starts the main loop.
    """
    args:argparse.Namespace = get_argparse()
    input_file:str = args.input_file
    root_directory_name:str = args.root_directory

    project_root = get_parent_path()
    input_file = project_root / "data" / input_file
    output_file = project_root / "directory_tree.txt"

    # TODO: The following line is not actually used yet, but will be once the program has different
    #   ways to 'start' the program.
    check_for_output_file(output_file)

    # TODO: eventually, this will need to be changed to checking if a directory is already populated
    #   for now, this will just be the entry point.
    with open(input_file, "r") as file:
        directories = file.read().strip()

    # Populating the root directory.
    main_directory_asset = instantiate_directory_object(parent_directory_name=root_directory_name, directory_list=directories)

    # Entering the main loop.
    navigator = DirectoryNavigator(main_directory_asset)


def get_argparse() -> argparse.Namespace:
    """Grabs the command-line arguments.

    :returns: The arguments given when starting the program.
    :rtype: argparse.Namespace
    """
    argparse_description = """\
    A manual web application spidering program.
    The reason this is manual is to prevent automated spidering tools from unintentionally corrupting or defacing an object if it automatically fills out forms.

    If this is your first time running this applicaiton, preform the following:
    1. Run src/walkman.js inside of the web application you are spidering.
    2. Right-click on the generated list in the console and click on 'copy Object.'
    3. Create 'input.txt' inside of the data folder.
    4. Paste the results inside of input.txt. It should look like a list.
    5. Run this program without any arguments.
    6. Follow the prompt to do more things :).
    """

    parser = argparse.ArgumentParser(description=textwrap.dedent(argparse_description), 
                                     formatter_class=argparse.RawDescriptionHelpFormatter
                                     )

    parser.add_argument("-i", "--input_file", 
                        help="The input file when building the root directory. DEFAULTS to input.txt", 
                        default="input.txt"
                        )

    parser.add_argument("-r", "--root_directory",
                        help="The name of the root directory. DEFAULTS to /",
                        default="/"
                        )

    return parser.parse_args()


def get_parent_path() -> "PosixPath":
    """Grabs the root directory of the project.

    :returns: The path to the project's directory.
    :rtype: PosixPath
    """
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    return project_root


def check_for_output_file(output_file:"PosixPath"):
    """Not currently used.

    When used, this will check for an output file. If it exists, then it will load the data.
    """
    # TODO: Check if user wants to load data, then do some validation and loading
    return output_file.resolve().exists()


def instantiate_directory_object(parent_directory_name, directory_list) -> DirectoryAsset:
    """Creates the root directory and populates it's children.

    :returns: The root directory that is populated with children directories.
    :rtype: DirectoryAsset
    """
    directory_asset = DirectoryAsset(name=parent_directory_name, level=2)
    directory_asset.populate_directories(directory_list)
    return directory_asset


if __name__ == "__main__":
    main()
