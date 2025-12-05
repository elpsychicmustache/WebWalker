import curses
import subprocess

from directory_asset import DirectoryAsset, get_datafile

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
        :param stdscr: The curses window to display and grab input.
        :type stdscr: curses.window
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

    def show_banner(self, y:int=0, x:int=0, message:str=None, reverse:bool=True) -> int:
        """Show a banner to stdout to user.

        This method is more of a helper method, and standardizes some of the banners, such as header and exit banners. If a message is not provided,
        it tries to best guess what the message to display is. If y and x are 0, then it shows the header banner. If y is of any value other value,
        then it informs the user to press enter to quit.

        :param y: The line to which display the message. DEFAULTS to 0.
        :type y: int
        :param x: The column to display the message. DEFAULTS to 0.
        :type x: int
        :param message: The message to display to the user. DEFAULTS to None.
        :type message: str
        :param reverse: If the message should display in reverse colors. DEFAULTS to True.
        :type reverse: bool
        :returns: The length of the message.
        :rtype: int
        """
        if message:
            self.stdscr.addstr(y, x, message, curses.A_REVERSE if reverse else curses.A_NORMAL)
        else:
            # Attempt to best guess what message the user wants to display:
            if y==0 and x==0:
                message = f"[+] Currently in '{self.current_directory.name}': {len(DirectoryAsset.master_list)} directories exist"
            else:
                message = "Press ENTER ... "
            self.stdscr.addstr(y, x, message, curses.A_REVERSE if reverse else curses.A_NORMAL)

        return len(message)

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
                ("Populate current directory", self.populate_current_directory),
                ("Populate child directory", self.populate_child_directory),
                ("Add a child directory", self.add_child_directory),
                ("Change to a directory", self.change_directory),
                ("Save directory tree", self.save_directory),
                ("Remove a child directory", self.remove_child_directory),
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
        self.show_banner()

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

        # This block of code is needed to handle directories with no children.
        try:
            directory_list = self.current_directory.get_asset_list()
        except IndexError as e:
            self.stdscr.addstr(0, 0, str(e), self.RED_ALERT)
            exit_banner = "Press ENTER ..."
            self.stdscr.addstr(1, 0, exit_banner)
            self.stdscr.getch(1, len(exit_banner))
            return  # exit this function

        # Determines how many directory lines can be shown at once.
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

                col_length:int = self.show_banner(y=last_available_line, x=0,
                                                  message=f"{index + 1} out of {len(directory_list)} directories printed. Print any key to continue or q to quit."
                                                  )
                self.stdscr.refresh()
                current_print_line = 0
                # If user's key input is q, then quit
                if self.stdscr.getkey(last_available_line, col_length).lower() == "q":
                    self.stdscr.clear()
                    return
                self.stdscr.clear()

        col_length:int = self.show_banner(y=last_available_line, x=0, message=f"All directories printed. Press any key to exit.")

        self.stdscr.refresh()
        self.stdscr.getch(last_available_line, col_length)

    def populate_current_directory(self) -> None:
        self.stdscr.clear()

        self.show_banner()

        # Get the file name.
        input_banner = f"[+] Please enter the name of the file to populate the current directory: "
        col_length = self.show_banner(1, 0, input_banner, reverse=False)
        file_name:str = self.stdscr.getstr(1, col_length).decode()

        input_file = get_datafile(file_name)  # function from directory_asset
        self.current_directory.populate_directories(input_file)

    def populate_child_directory(self) -> None:
        """Calling this method evokes the populate_child_directories() for the current_directory attribute.

        The method should walk the user through creation of the child directory, based on the directory name and the input file's name.

        File path and name validation is inside directory_asset.
        """
        self.stdscr.clear()

        # This block of code grabs and handles getting the child's name.
        input_banner = "[+] Please enter the name of the child directory: "
        col_length = self.show_banner(message=input_banner, reverse=False)
        child_name:str = self.stdscr.getstr(0, col_length).decode()

        if not self.current_directory.children.get(child_name):
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[!] {child_name} is not a valid child directory. Nothing happened ...", self.RED_ALERT)
            # TODO: Ask if user wants to create the directory. Before doing so, the directory needs to be checked against the master list.
            col_length = self.show_banner(y=1, x=0)
            self.stdscr.getch(1, col_length)
            return  # end this function

        # This block of code grabs the input file name.
        file_input_banner = "[+] Please enter the name of the file from which to populate the directory: "
        col_length = self.show_banner(1, 0, message=file_input_banner, reverse=False)
        file_name:str = self.stdscr.getstr(1, col_length).decode()

        # Tell the user the file was found and children populated, or file was not found.
        try:
            self.current_directory.populate_child_directories(child_name, file_name)
        except FileNotFoundError:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[!] {file_name} is not a valid file - please double check file name", self.RED_ALERT)
            self.stdscr.refresh()
        else:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[+] {child_name} directories have been populated!", self.GREEN_ALERT)
        finally:
            col_length = self.show_banner(y=1, x=0)
            self.stdscr.getch(1, col_length)

    def add_child_directory(self) -> None:
        """Creates a single child directory to current_directory.

        This calls the add_child() method for the current_directory object.
        Interaction and child object creation is implemented in this function.
        """
        # Show the user what directory they are in.
        self.stdscr.clear()
        self.show_banner()

        input_message = "Please enter the child's name: "
        col_length = self.show_banner(y=1, x=0, message=input_message, reverse=False)
        child_name = self.stdscr.getstr(1, col_length).decode()

        try:
            child = DirectoryAsset(name=child_name, parent=self.current_directory, level=self.current_directory.level+2)
        except ValueError as e:
            self.stdscr.addstr(2, 0, str(e), self.RED_ALERT)
            closing_message = "Nothing happened. Press ENTER ..."
            col_length = self.show_banner(y=3, x=0, message=closing_message)
            self.stdscr.getch(3, col_length)
        else:
            self.current_directory.add_child(child)

            self.stdscr.addstr(2, 0, f"[+] {child_name} has been added to {self.current_directory.name}", self.GREEN_ALERT)
            col_length = self.show_banner(y=3, x=0)
            self.stdscr.getch(3, col_length)

    def change_directory(self) -> None:
        """Changes the current_directory attribute.

        Nothing will happen if the directory being called does not exist in the master_list of DirectoryAsset.
        """
        self.stdscr.clear()
        self.show_banner()
        new_directory_prompt = "[+] Please enter the name of the directory to change to: "
        col_length = self.show_banner(y=1, x=0, message=new_directory_prompt, reverse=False)
        new_directory_name = self.stdscr.getstr(1, col_length).decode()

        try:
            directory_location:int = [x.name for x in DirectoryAsset.master_list].index(new_directory_name)
        except ValueError:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[!] '{new_directory_name}' is not a recognized directory. Nothing happened.", self.RED_ALERT)
        else:
            self.current_directory = DirectoryAsset.master_list[directory_location]
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"[+] Successfully changed to '{new_directory_name}'.", self.GREEN_ALERT)

        col_length = self.show_banner(y=1, x=0)
        self.stdscr.getch(1, col_length)

    def save_directory(self) -> None:
        """Save the current directory tree to a file.

        This method prompts the user for the name of a file to save the directory tree to.
        This file defaults to 'output.txt' if nothing is provided, and will be saved inside of the 'data' folder
        of the project's root directory.
        """
        self.stdscr.clear()

        # Show user current directory information.
        self.show_banner()

        input_banner = "[+] Please enter the name of the output file (default 'output.txt'): "
        col_length = self.show_banner(1, 0, input_banner, reverse=False)
        file_name = self.stdscr.getstr(1, col_length).decode()

        if file_name:
            self.stdscr.addstr(2, 0, f"Saving to data/{file_name}...")
            self.current_directory.create_output_file(output_file_name)
            self.stdscr.addstr(3, 0, f"[+] Saved to data/{file_name}!", self.GREEN_ALERT)
        else:
            self.stdscr.addstr(2, 0, "Saving to data/outputfile.txt ...")
            self.current_directory.create_output_file()
            self.stdscr.addstr(3, 0, f"[+] Saved to data/outputfile.txt", self.GREEN_ALERT)

        col_length = self.show_banner(y=4, x=0)
        self.stdscr.getch(4, col_length)

    def remove_child_directory(self) -> None:
        self.stdscr.clear()
        self.show_banner()

        input_banner = "[+] Please enter the name of the child directory to remove: "
        col_length = self.show_banner(1, 0, input_banner, reverse=False)
        child_name = self.stdscr.getstr(1, col_length).decode()

        try:
            self.current_directory.remove_child(child_name)
        except ValueError as e:
            self.stdscr.addstr(2, 0, str(e), self.RED_ALERT)
        else:
            self.stdscr.addstr(2, 0, f"Removed {child_name} from {self.current_directory.name}", self.GREEN_ALERT)
        finally:
            col_length = self.show_banner(3, 0)
            self.stdscr.getch(3, col_length)

    def quit_program(self) -> None:
        """Clears the screen.

        This doesn't actually quit the program, but simply calls the curses clear() function.
        The quitting is handled by the enter_main_loop() method. This method is being kept in 
        case future clean up is needed before actually quitting the program. It is also required
        to follow the main_menu attribute convention by having a function to call. None causes an error.
        """
        self.stdscr.clear()
