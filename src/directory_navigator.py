import subprocess

from directory_asset import DirectoryAsset

def clear_screen():
    subprocess.run("clear")

class DirectoryNavigator:
    def __init__(self, current_directory:DirectoryAsset) -> None:
        self.main_options = {
                1: ["Show directory tree", self.show_current_directory_tree],
                2: ["Populate child directory", self.populate_child_directory]
                # 3: ["Change directory", self.change_directory]
                }

        self.current_directory = current_directory

        self.show_main_menu()

    def show_current_directory_tree(self) -> None:
        print(f"[+] Currently in '{self.current_directory.name}'")

        self.current_directory.print_asset_list()

        input("Press ENTER . . .")

        self.show_main_menu()

    def populate_child_directory(self) -> None:
        pass

    def show_main_menu(self) -> None:
        clear_screen()

        print(f"[+] Currently in '{self.current_directory.name}'")
        for (key, option) in self.main_options.items():
            print(f"{key} - {option[0]}")
