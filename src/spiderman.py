import argparse
import curses
import textwrap

from pathlib import Path

from directory_asset import DirectoryAsset
from directory_navigator import DirectoryNavigator


def main(stdscr) -> None:
    """Running this starts the program.

    Running without any arguments causes the program to grab the input file,
    which shoud be '../data/input.txt'
    Using the above file, the program creates the root directory as '/' and then populates children
    directories that are specified in the aforementioned input file (which creates a directory tree).
    Lastly, it creates the DirectoryNavigator object, which starts a loop that allows the user
    to interact with the directory tree.

    Other arguments can be provided which will change what happens. Run -h to learn more.

    :param stdscr: The curses instantiation from curses.wrapper()
    :stdscr type: curses.window
    """
    args:argparse.Namespace = get_argparse()
    root_directory_name:str = args.root_directory
    output_file:str = args.output_file
    DirectoryAsset.hostname = args.hostname

    project_root:"PosixPath" = get_parent_path()
    directories:str = None

    # if input_file or input_tree was provided, populate directories with the data
    if args.input_file or args.input_tree:
        input_file:"PosixPath" = project_root / "data" / (args.input_file if args.input_file else args.input_tree)
        with open(input_file, "r") as file:
            directories:str = file.read().strip()

    # If input_tree was provided, then perform the appropriate parsing on directories
    # because directories won't work as is (because it is not None and not in the format from walkman.js).
    if args.input_tree:
        directory_list:list[str] = directories.split("\n")
        parent_child_dict = parse_directory_list(directory_list)
        # populate the first directory
        first_key = next(iter(parent_child_dict))
        main_directory_asset:DirectoryAsset = instantiate_directory_object(parent_directory_name=first_key, directory_list="\n".join(parent_child_dict[first_key]))
        del parent_child_dict[first_key]

        # populate the rest of the dictionaries
        for parent, children in parent_child_dict.items():
            directory_names:list[str] = [directory.name for directory in DirectoryAsset.master_list]
            parent_index:int = directory_names.index(parent)
            parent_directory:DirectoryAsset = DirectoryAsset.master_list[parent_index]
            parent_directory.populate_directories("\n".join(children))

    # Else, populate the root directory.
    else:
        main_directory_asset:DirectoryAsset = instantiate_directory_object(parent_directory_name=root_directory_name, directory_list=directories)
    # if output_file was provided, then generate outputfile. Otherwise run main loop.
    if args.output_file:
        main_directory_asset.create_output_file(output_file_name=output_file)
    else:
        navigator = DirectoryNavigator(main_directory_asset, stdscr)


def parse_directory_list(directory_list:list[str]) -> dict[str, list[str]]:
    """Parse the current output format in a way that can rebuild it as DirectoryAsset objects.

    God be with ye if you must update this. It took a while to figure out how to make this work.
    Either way, provide it with a list (newline separated) from a DirectoryAsset output file.

    This then figures out the hierarchies and saves them so the directory file can be worked on
    after quitting the program. There is probably a much easier way of doing this, especially
    if we can just create DirectoryAsset objects right in this function.

    :param directory_list: The output file from directory_asset, but split by newlines.
    :type directory_list: list[str]
    :returns: A parent directory (as a string), with a list of children directories (as strings)
    :rtype: dict[str, list[str]]
    """
    # dictionary should be in style {parent: [children]}
    # directory_pointer should be in style {int, parent}
    # The directory_pointer points to what the parent is for a given level
    parent_child_dict:dict[str, list[str]] = {}
    directory_pointer:dict[int, str] = {}

    previous_level:int = 0
    current_level:int = 0

    # Sorry for the comment offense in the following lines, but this took a while to figure out
    for index, directory in enumerate(directory_list):
        # find the current parent-child hierarchy by the location of "-"
        # then, remove the "-" and strip all whitespace to get only the directory name
        current_level = directory.find("-")
        directory = directory.replace("-", "", 1).strip()

        # if parent_child_dict does not exist, create it (should only happen first loop)
        if not parent_child_dict:
            parent_child_dict[directory] = []
            directory_pointer[current_level] = directory

        # If we have entered a new hierarchy
        elif current_level > previous_level:
            # check if dictionary previous_level exists
            parent:str = directory_pointer.get(previous_level)
            # if so, then populate parent_child_dict as child to parent
            # this prevents duplicate parent entries
            if parent_child_dict.get(parent):
                parent_child_dict[parent].append(directory)
            # else, create directory_pointer entry with previous_level
            else:
                # get previous index's cleaned directory name, and create directory_pointer
                previous_directory:str = directory_list[index-1].replace("-", "", 1).strip()
                directory_pointer[previous_level] = previous_directory
                # then create parent_child_dict and append to that
                parent_child_dict[previous_directory] = []
                parent_child_dict[previous_directory].append(directory)
        # If current_level is same as previous_level, populate the highest level from directory_pointer
        # since we are at the same hierarchy
        elif current_level == previous_level:
            max_key = max(directory_pointer, key=directory_pointer.get)
            parent:str = directory_pointer.get(max_key)
            parent_child_dict[parent].append(directory)
        # If current_level is less than previous_level, we have gone back a hierarchy level
        # which means we need to delete the highest level from directory_pointer,
        # grab the new highest level (after deleting) which allows us to
        # populate the directory from our previous hiearchy
        elif current_level < previous_level:
            current_max_key = max(directory_pointer, key=directory_pointer.get)
            del directory_pointer[current_max_key]
            new_max_key = max(directory_pointer, key=directory_pointer.get)
            parent:str = directory_pointer[new_max_key]
            parent_child_dict[parent].append(directory)

        previous_level = current_level

    return parent_child_dict


def get_argparse() -> argparse.Namespace:
    """Grabs the command-line arguments specified when the program was evoked.

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
                        help="The input file when building the root directory.", 
                        default=None
                        )

    parser.add_argument("-I", "--input_tree",
                        help="Use this option to build the tree from the output file of a previously created tree. Cannot be used with -i.",
                        default=None
                        )

    parser.add_argument("-r", "--root_directory",
                        help="The name of the root directory. DEFAULTS to /",
                        default="/"
                        )

    parser.add_argument("-o", "--output_file",
                        help="The output file for the tree. If used, the program does not run interactive directory building.",
                        default=None)

    parser.add_argument("-H", "--hostname",
                        help="The host or target name. Used to remove hostname from url paths so they can be shortened from limited screen space.",
                        default=None)

    args = parser.parse_args()

    # Checking and updating parameters based on what switches and arguments were provided.
    check_args_combinations(args)

    return args


def check_args_combinations(args:argparse.Namespace) -> None:
    """Checks args and performs validation, error raising, or other logic problems for args.

    :param args: The arguments grabbed from argparse.
    :type args: argparse.Namespace
    """
    if args.input_tree and args.input_file:
        raise ValueError("[!] Cannot use --input_tree [-I] and --input_file [-i] at the same time.")


def get_parent_path() -> "PosixPath":
    """Grabs the root directory of the project.

    This is needed to get to the data folder and other needed resources.

    :returns: The path to the project's directory.
    :rtype: PosixPath
    """
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    return project_root


def instantiate_directory_object(parent_directory_name:str, directory_list:str) -> DirectoryAsset:
    """Creates the 'root' directory_asset and populates it's children if provided.

    :param parent_directory_name: The name of the root directory.
    :type parent_directory_name: str
    :param directory_list: The string object containing a list of children from walkman.js.
    :type directory_list: str
    :returns: The root directory that is populated with children directories.
    :rtype: DirectoryAsset
    """
    directory_asset = DirectoryAsset(name=parent_directory_name, level=2)

    # only run the following code if directory_list is populated
    if directory_list:
        directory_asset.populate_directories(directory_list)
    return directory_asset


if __name__ == "__main__":
    # Not super efficient, but calling args before curses is called.
    # This way, help can be ran before curses takes over stdout.
    # Args will also be called inside of main.
    args = get_argparse()
    curses.wrapper(main)
