from pathlib import Path

class DirectoryAsset():
    master_list = []

    def __init__(self, name:str, level:int, parent:"DirectoryAsset"=None, children:dict[str, "DirectoryAsset"]=None) -> None:
        self.name = name
        self.level = level  # recommended to start with 2
        self.parent = parent
        self.children = children or {}

        DirectoryAsset.master_list.append(self)  # keeping track of a master list to prevent recursive entries

    def populate_directories(self, directory_string_list:str) -> None:
        directories = set(
                directory_string_list
                .replace("[", "")
                .replace("]", "")
                .replace(",", "")
                .replace('"', "")
                .replace(" ", "")
                .strip()
                .split("\n")
                )

        directories_to_add = set()

        for directory in directories:
            if directory == self.name:
                continue
            elif "#" in directory:
                continue
            elif directory in [x.name for x in DirectoryAsset.master_list]:
                continue
            else:
                directories_to_add.add(directory)

        for directory in directories_to_add:
            child_directory = DirectoryAsset(directory, level=self.level+2, parent=self)
            self.add_child(child_directory)

        # sorting children directories by alphabetical order
        self.children = dict(sorted(self.children.items()))

    def print_asset_list(self) -> None:
        if not self.parent:
            print("- " + self.name)  # needed to prevent double printing of the directory name
        if not self.children:
            print(f"[!] No subdirectories found for {self.name}")
            return  # exit the function

        for directory in self.children.keys():
            print(" " * self.level, end="")
            print("- " + directory)
            if self.children[directory].children:
                self.children[directory].print_asset_list()

    def add_child(self, child:"DirectoryAsset"=None) -> "DirectoryAsset":
        # TODO: child=None should be handled differently; i.e. interactively created
        child.parent_directory = self

        return self.children.setdefault(child.name, child)

    def populate_child_directories(self) -> None:
        child_name = input("Please enter the child directory name: ")

        if not self.children.get(child_name):
            raise KeyError(f"[!] {child_name} is not a valid directory of {self.name}")

        file_input_name = input("Please enter the input file name: ")

        data_path = Path(__file__).resolve().parent.parent / "data" / file_input_name

        with open(data_path, "r") as file:
            directories = file.read().strip()

        self.children[child_name].populate_directories(directories)

    def remove_child() -> None:
        pass
