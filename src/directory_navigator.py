import subprocess

from directory_asset import DirectoryAsset

def _clear_screen() -> None:
    """Clears the stdout screen."""
    subprocess.run("clear")


def _enter_to_continue() -> None:
    """Pauses the program by asking the user to press ENTER to continue"""
    input("Press ENTER to continue...")


class DirectoryNavigator:
    def __init__(self, current_directory:DirectoryAsset) -> None:
        """Creates a looping interface for handling DirectoryAsset objects.

        When this object is created, a looping menu occurs, which allows direct interaction
        with DirectoryAsset objects. Since the DirectoryAsset module is built as a composition
        design, this class is a helpful interface for interacting with all the objects.

        :param current_directory: The DirectoryAsset that should be the 'focal' point for the navigator.
        :type current_directory: DirectoryAsset
        """
        self.main_options = self.create_options_menu()

        self.current_directory = current_directory

        self.enter_main_loop()

    def create_options_menu(self) -> dict[int, tuple]:
        """Calling this method creates the main menu options as a dictionary.

        The main menu options may change overtime. Not having an automated way of handling this
        becomes troublesome. Hence, this method does this exact automation, while keeping the quit
        option as the last option.

        :returns: A dictionary with the key (or option) as an int, and then a tuple
        which contains the description of the funciton, as well as the function to call.
        :rtype: dict[int, tuple]
        """
        options = [
                ("Show directory tree", self.show_current_directory_tree),
                ("Populate child directory", self.populate_child_directory),
                ("Add a directory", self.add_child_directory),
                ("Change directory", self.change_directory),
                # Add any options above "Quit" - that way, quit is last
                ("Quit", self.quit_program)
                ]

        return {option_number: option_tuple for option_number, option_tuple in enumerate(options, start=1)}

    def enter_main_loop(self):
        """Calling this evokes the main loop for DirectoryNavigator.

        This loops continuously until the user provides the quite option, or an
        unhandled error occurs.
        """
        # TODO: Implement input validation.
        self.show_main_menu()
        option = int(input("[+] Please enter the option: "))  # must be an int
        self.main_options.get(option)[1]()  # [1] is the function, so must use () to call the function
        while option != max(self.main_options.keys()):
            self.show_main_menu()
            option = int(input("[+] Please enter the option: "))
            self.main_options[option][1]()

    def show_current_directory_tree(self) -> None:
        """This method shows the current directory tree.

        This produces the tree from the perspective of the current_directory attribute.
        This means that any parent directories are ignored. To show all directories,
        it is recommended to be in the root directory.
        """
        _clear_screen()

        self.current_directory.print_asset_list()

        input("Press ENTER . . .")

    def show_main_menu(self) -> None:
        """Displays the main menu options."""
        _clear_screen()

        print(f"[+] Currently in '{self.current_directory.name}': {len(DirectoryAsset.master_list)} directories exist")
        for (key, option) in self.main_options.items():
            print(f"{key} - {option[0]}")

    def populate_child_directory(self) -> None:
        """Calling this method evokes the populate_child_directories() for the current_directory attribute.

        Actual interaction occurs in the populate_child_directories() method.
        """
        _clear_screen()
        # TODO: Move functionality from populate_child_directories to this method.
        self.current_directory.populate_child_directories()

    def add_child_directory(self) -> None:
        """Creates a single child directory to current_directory.

        This calls the add_child() method for the current_directory object.
        Interaction and child object creation is implemented in this function.
        """
        child_name = input("Please enter the child's name: ")
        child = DirectoryAsset(name=child_name, parent=self.current_directory, level=self.current_directory.level+2)
        self.current_directory.add_child(child)

    def change_directory(self) -> None:
        """Changes the current_directory attribute.

        Nothing will happen if the directory being called does not exist in the master_list of DirectoryAsset.
        """
        new_directory_name = input("[+] Please enter the name of the directory to change to: ")
        try:
            directory_location:int = [x.name for x in DirectoryAsset.master_list].index(new_directory_name)
        except ValueError:
            print(f"[!] '{new_directory_name}' is not a recognized directory.")
        else:
            self.current_directory = DirectoryAsset.master_list[directory_location]
            print(f"Successfully changed to '{new_directory_name}'.")

        input("Press ENTER ... ")

    def quit_program(self) -> None:
        """Clears the screen.

        This doesn't actually quit the program, but simply calls the _clear_screen() function.
        The quitting is handled by the enter_main_loop() method. This method is being kept in 
        case future clean up is needed before actually quitting the program. It is also required
        to follow the main_menu attribute convention by having a function to call. None causes an error.
        """
        _clear_screen()
