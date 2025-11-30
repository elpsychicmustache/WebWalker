import curses
import subprocess

from directory_asset import DirectoryAsset

def _clear_screen() -> None:
    """Clears the stdout screen."""
    subprocess.run("clear")


def _enter_to_continue() -> None:
    """Pauses the program by asking the user to press ENTER to continue"""
    input("Press ENTER to continue...")


class DirectoryNavigator:
    def __init__(self, current_directory:DirectoryAsset, stdscr:"curses.window") -> None:
        """Creates a looping interface for handling DirectoryAsset objects.

        When this object is created, a looping menu occurs, which allows direct interaction
        with DirectoryAsset objects. Since the DirectoryAsset module is built as a composition
        design, this class is a helpful interface for interacting with all the objects.

        :param current_directory: The DirectoryAsset that should be the 'focal' point for the navigator.
        :type current_directory: DirectoryAsset
        """
        self.main_options = self.create_options_menu()

        # Setting curses parameters
        self.stdscr = stdscr
        curses.echo(True)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        self.GREEN_ALERT = curses.color_pair(1)
        self.RED_ALERT = curses.color_pair(2)

        self.current_directory = current_directory

        # starts an 'infinite' loop
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
                ("Save directory tree", self.save_directory),
                # Add any options above "Quit" - that way, quit is last
                ("Quit", self.quit_program)
                ]

        return {option_number: option_tuple for option_number, option_tuple in enumerate(options, start=1)}

    def enter_main_loop(self):
        """Calling this evokes the main loop for DirectoryNavigator.

        This loops continuously until the user provides the quit option, or an
        unhandled error occurs.
        """
        self.stdscr.clear()
        current_display_line = self.show_main_menu()

        # The following lines get the users input.
        input_display = "[+] Please enter your option: "
        self.stdscr.addstr(current_display_line, 0, input_display)
        option = self.stdscr.getkey(current_display_line, len(input_display)) # show cursor after input_display
        option = int(option)

        self.stdscr.refresh()

        # self.main_options.get(option)[1]()  # [1] is the function, so must use () to call the function
        while option != max(self.main_options.keys()):
            # run the function that was requested
            self.main_options[option][1]()

            self.stdscr.clear()
            # reshow main menu
            current_display_line = self.show_main_menu()

            # The following lines get the users input.
            input_display = "[+] Please enter your option: "
            self.stdscr.addstr(current_display_line, 0, input_display)
            option = self.stdscr.getkey(current_display_line, len(input_display)) # show cursor after input_display
            option = int(option)

    def show_main_menu(self) -> int:
        """Displays the main menu options."""
        #_clear_screen()
        banner = f"[+] Currently in '{self.current_directory.name}': {len(DirectoryAsset.master_list)} directories exist"
        self.stdscr.addstr(0,0, banner, curses.A_REVERSE)

        current_display_line:int = 1

        for (key, option) in self.main_options.items():
            self.stdscr.addstr(current_display_line, 0, f"{key} - {option[0]}")
            current_display_line += 1

        return current_display_line

    def show_current_directory_tree(self) -> None:
        """This method shows the current directory tree.

        This produces the tree from the perspective of the current_directory attribute.
        This means that any parent directories are ignored. To show all directories,
        it is recommended to be in the root directory.
        """
        self.stdscr.clear()

        directory_list = self.current_directory.get_asset_list()

        last_available_line = curses.LINES - 1

        # The following lines print the directories to the screen, one window at a time.
        current_print_line = 0
        for index in range(len(directory_list)):
            if current_print_line < last_available_line-1:  # keeping last_available_line for status
                self.stdscr.addstr(current_print_line, 0, directory_list[index])
                current_print_line += 1
            else:
                # Printing the last directory that can be shown here; otherwise, we lose 1 directory every refresh
                # due to the else statement still incrementing index
                self.stdscr.addstr(current_print_line, 0, directory_list[index])
                self.stdscr.addstr(last_available_line, 0, 
                                   f"{index + 1} out of {len(directory_list)} directories printed. Print any key to continue.", 
                                   curses.A_REVERSE
                                   )
                self.stdscr.refresh()
                current_print_line = 0
                self.stdscr.getch()
                self.stdscr.clear()

        self.stdscr.addstr(last_available_line, 0,
                           f"All directories printed. Press any key to exit.",
                           curses.A_REVERSE
                           )

        self.stdscr.refresh()
        self.stdscr.getch()

    def populate_child_directory(self) -> None:
        """Calling this method evokes the populate_child_directories() for the current_directory attribute.

        The method should walk the user through creation of the child directory, based on the directory name and the input file's name.

        File path and name validation is inside directory_asset.
        """
        self.stdscr.clear()

        input_banner = "[+] Please enter the name of the child directory: "
        self.stdscr.addstr(0, 0, input_banner)
        child_name:str = self.stdscr.getstr(0, len(input_banner)).decode()

        if not self.current_directory.children.get(child_name):
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[!] {child_name} is not a valid child directory. Nothing happened ...", self.RED_ALERT)
            # TODO: Ask if user wants to create the directory. Before doing so, the directory needs to be checked against the master list.
            self.stdscr.getch(1, 0)
            return  # end this function

        file_input_banner = "[+] Please enter the name of the file from which to populate the directory: "
        self.stdscr.addstr(1, 0, file_input_banner)
        file_name:str = self.stdscr.getstr(1, len(file_input_banner)).decode()

        self.current_directory.populate_child_directories(child_name, file_name)

        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"[+] {child_name} directories have been populated!", self.GREEN_ALERT)
        closing_message = "Press ENTER ..."
        self.stdscr.addstr(1, 0, closing_message)
        self.stdscr.getch(1, len(closing_message))

    def add_child_directory(self) -> None:
        """Creates a single child directory to current_directory.

        This calls the add_child() method for the current_directory object.
        Interaction and child object creation is implemented in this function.
        """
        self.stdscr.clear()
        banner = f"[+] Currently in '{self.current_directory.name}': {len(DirectoryAsset.master_list)} directories exist"
        self.stdscr.addstr(0,0, banner, curses.A_REVERSE)

        input_message = "Please enter the child's name: "
        self.stdscr.addstr(1, 0, input_message)
        child_name = self.stdscr.getstr(1, len(input_message)).decode()
        child = DirectoryAsset(name=child_name, parent=self.current_directory, level=self.current_directory.level+2)
        self.current_directory.add_child(child)

        self.stdscr.addstr(2, 0, f"[+] {child_name} has been added to {self.current_directory.name}", self.GREEN_ALERT)
        closing_message = "Press ENTER ..."
        self.stdscr.addstr(3, 0, closing_message)
        self.stdscr.getch(3, len(closing_message))

    def change_directory(self) -> None:
        """Changes the current_directory attribute.

        Nothing will happen if the directory being called does not exist in the master_list of DirectoryAsset.
        """
        self.stdscr.clear()
        new_directory_prompt = "[+] Please enter the name of the directory to change to: "
        self.stdscr.addstr(0, 0, new_directory_prompt)
        new_directory_name = self.stdscr.getstr(0, len(new_directory_prompt)).decode()

        try:
            directory_location:int = [x.name for x in DirectoryAsset.master_list].index(new_directory_name)
        except ValueError:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[!] '{new_directory_name}' is not a recognized directory. Nothing happened.", self.RED_ALERT)
        else:
            self.current_directory = DirectoryAsset.master_list[directory_location]
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[+] Successfully changed to '{new_directory_name}'.", self.GREEN_ALERT)

        closing_message = "Press ENTER ..."
        self.stdscr.addstr(1, 0, closing_message)
        self.stdscr.getch(1, len(closing_message))

    def save_directory(self) -> None:
        self.stdscr.clear()

        banner = f"[+] Currently in '{self.current_directory.name}': {len(DirectoryAsset.master_list)} directories exist"
        self.stdscr.addstr(0,0, banner, curses.A_REVERSE)

        input_banner = "[+] Please enter the name of the output file (default 'output.txt'): "
        self.stdscr.addstr(1, 0, input_banner)
        file_name = self.stdscr.getstr(1, len(input_banner)).decode()

        if file_name:
            self.stdscr.addstr(2, 0, f"Saving to data/{file_name}...")
            self.current_directory.create_output_file(output_file_name)
            self.stdscr.addstr(3, 0, f"[+] Saved to data/{file_name}!", self.GREEN_ALERT)
        else:
            self.stdscr.addstr(2, 0, "Saving to data/outputfile.txt ...")
            self.current_directory.create_output_file()
            self.stdscr.addstr(3, 0, f"[+] Saved to data/outputfile.txt", self.GREEN_ALERT)

        closing_banner = "Press ENTER ..."
        self.stdscr.addstr(4, 0, closing_banner)
        self.stdscr.getch(4, len(closing_banner))

    def quit_program(self) -> None:
        """Clears the screen.

        This doesn't actually quit the program, but simply calls the curses clear() function.
        The quitting is handled by the enter_main_loop() method. This method is being kept in 
        case future clean up is needed before actually quitting the program. It is also required
        to follow the main_menu attribute convention by having a function to call. None causes an error.
        """
        self.stdscr.clear()
