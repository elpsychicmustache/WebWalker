class DirectoryAsset():
    def __init__(self, this_directory:str, child_directories:set[str]=None) -> None:
        self.this_directory = this_directory
        self.child_directories = child_directories

    def populate_directories(self, directory_list:str, running_directory_list:list[str]) -> None:
        directories = set(
                directory_list
                .replace("[", "")
                .replace("]", "")
                .replace(",", "")
                .replace('"', "")
                .replace(" ", "")
                .strip()
                .split("\n")
                )

        self.child_directories = sorted(directories)

    def print_asset_list(self) -> None:
        print("- " + self.this_directory)
        for directory in self.child_directories:
            print("  - " + directory)
