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
    # Grabbing parameters from argparse
    args:argparse.Namespace = get_argparse()
    root_directory_name:str = args.root_directory
    output_file:str = args.output_file
    DirectoryAsset.hostname = args.hostname
    # Stating some additional variables
    project_root:"PosixPath" = get_parent_path()
    directories:str = None
    valid_file_found = True  # controls functionality

    # clearing screen
    stdscr.clear()

    # if input_file or input_tree was provided, populate directories with the data
    try:
        if args.input_file or args.input_tree:
            input_file:"PosixPath" = project_root / "data" / (args.input_file if args.input_file else args.input_tree)
            with open(input_file, "r") as file:
                directories:str = file.read().strip()
    except FileNotFoundError:
        stdscr.addstr(0, 0, f"[!] {input_file} was not found. Populating an empty directory.", curses.COLOR_RED)
        stdscr.addstr(1, 0, "Press ENTER ...", curses.A_REVERSE)
        stdscr.getch()
        valid_file_found = False

    # If input_tree was provided and an error did not occur with input file, then perform the appropriate parsing on directories
    # because directories won't work as is (because it is not None and not in the format from walkman.js).
    if args.input_tree and valid_file_found:
        directory_list:list[str] = directories.split("\n")
        try:
            main_directory_asset:DirectoryAsset = parse_directory_list(directory_list)
        except AttributeError:
            stdscr.addstr(0, 0, f"[!] There appears to be something wrong with {input_file}. Populating an empty directory instead.", curses.COLOR_RED)
            stdscr.addstr(1, 0, "Press ENTER ...", curses.A_REVERSE)
            stdscr.getch()
            # clearing any created values, and then creating an empty directory
            DirectoryAsset.nuke_directory()
            main_directory_asset:DirectoryAsset = instantiate_directory_object(parent_directory_name=root_directory_name, directory_list=None)
    # Else, populate the root directory.
    else:
        main_directory_asset:DirectoryAsset = instantiate_directory_object(parent_directory_name=root_directory_name, directory_list=directories)

    # if output_file was provided, then generate outputfile (unless error occured). Otherwise run main loop.
    if args.output_file:
        main_directory_asset.create_output_file(output_file_name=output_file)
    else:
        navigator = DirectoryNavigator(main_directory_asset, stdscr)


def parse_directory_list(directory_list:list[str]) -> DirectoryAsset:
    """Parse the current output format in a way that can rebuild it as DirectoryAsset objects.

    This then figures out the hierarchies based on directory_list and saves them so the directory file can be worked on
    after quitting the program.

    :param directory_list: The output file from directory_asset, but split by newlines.
    :type directory_list: list[str]
    :returns: The root parent directory asset.
    :rtype: DirectoryAsset
    """
    previous_level:int = 0
    current_level:int = 0
    current_parent:DirectoryAsset = None

    # Sorry for the comment offense in the following lines, but this took a while to figure out
    for index, directory in enumerate(directory_list):
        # find the current parent-child hierarchy by the location of "-"
        # then, remove the "-" and strip all whitespace to get only the directory name
        current_level = directory.find("-")
        directory = directory.replace("-", "", 1).strip()

        # if master_list does not exist, create it (should only happen first loop)
        if not DirectoryAsset.master_list:
            current_parent = DirectoryAsset(directory)

        # If we have entered a new hierarchy
        # get previously created directory, and add current directory as a child
        elif current_level > previous_level:
            previous_directory_name:str = directory_list[index-1].replace("-", "", 1).strip()
            directory_index:int = [x.name for x in DirectoryAsset.master_list].index(previous_directory_name)
            current_parent = DirectoryAsset.master_list[directory_index]
            child_directory = DirectoryAsset(name=directory, level=current_parent.level+2, parent=current_parent)
            current_parent.add_child(child_directory)

        # If we are at the same hierarchy level,
        # then just populate directory as a child
        elif current_level == previous_level:
            child_directory = DirectoryAsset(name=directory, level=current_parent.level+2, parent=current_parent)
            current_parent.add_child(child_directory)

        # If current_level is less than previous_level, we have gone back a hierarchy level
        elif current_level < previous_level:
            current_parent = current_parent.parent
            child_directory = DirectoryAsset(name=directory, level=current_parent.level+2, parent=current_parent)
            current_parent.add_child(child_directory)

        previous_level = current_level

    # return the first indexed DirectoryAsset from master_list
    # because this should be the root directory
    return DirectoryAsset.master_list[0]


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
