import subprocess

from directory_asset import DirectoryAsset

def clear_screen():
    subprocess.run("clear")

class DirectoryNavigator:
    def __init__(self, current_directory:DirectoryAsset) -> None:
        self.main_options = {
                1: ["Show directory tree", self.show_current_directory_tree],
                2: ["Populate child directory", self.populate_child_directory],
                3: ["Add a directory", self.add_child_directory],
                4: ["Change directory", self.change_directory]
                }

        # Setting the quit option, which should be the last option of main_options
        quit_option = list(self.main_options.keys())[-1] + 1
        self.main_options[quit_option] = ["Quit", self.quit_program]

        self.current_directory = current_directory

        self.enter_main_loop()

    def enter_main_loop(self):
        # TODO: Implement input validation.
        self.show_main_menu()
        option = int(input("[+] Please enter the option: "))  # must be an int
        self.main_options.get(option)[1]()  # [1] is the function, so must use () to call the function
        while option != max(self.main_options.keys()):
            self.show_main_menu()
            option = int(input("[+] Please enter the option: "))
            self.main_options[option][1]()

    def show_current_directory_tree(self) -> None:
        clear_screen()

        self.current_directory.print_asset_list()

        input("Press ENTER . . .")

    def populate_child_directory(self) -> None:
        clear_screen()
        self.current_directory.populate_child_directories()

    def show_main_menu(self) -> None:
        clear_screen()

        print(f"[+] Currently in '{self.current_directory.name}': {len(DirectoryAsset.master_list)} directories exist")
        for (key, option) in self.main_options.items():
            print(f"{key} - {option[0]}")

    def add_child_directory(self) -> None:
        child_name = input("Please enter the child's name: ")
        child = DirectoryAsset(name=child_name, parent=self.current_directory, level=self.current_directory.level+2)
        self.current_directory.add_child(child)

    def change_directory(self) -> None:
        new_directory_name = input("[+] Please enter the name of the directory to change to: ")
        try:
            directory_location:int = [x.name for x in DirectoryAsset.master_list].index(new_directory_name)
        except ValueError:
            print(f"[!] {new_directory_name} is not a recognized directory.")
        else:
            self.current_directory = DirectoryAsset.master_list[directory_location]

        input("Press ENTER ... ")

    def quit_program(self) -> None:
        clear_screen()

        input("Thanks for using - press ENTER to quit...")

        clear_screen()
