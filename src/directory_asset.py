class DirectoryAsset():
    def __init__(self, name:str, level:int, parent:"DirectoryAsset"=None, children:dict[str, "DirectoryAsset"]=None) -> None:
        self.name = name
        self.level = level
        self.parent = parent
        self.children = children or {}

    def populate_directories(self, directory_string_list:str, running_directory_list:list[str]) -> None:
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
            else:
                directories_to_add.add(directory)

        for directory in directories_to_add:
            child_directory = DirectoryAsset(directory, level=self.level+2)
            self.add_child(child_directory)

        # sorting children directories by alphabetical order
        self.children = dict(sorted(self.children.items()))

    def print_asset_list(self) -> None:
        print("- " + self.name)
        for directory in self.children.keys():
            print("  - " + directory)
            if self.children[directory].children:
                self.children[directory].print_asset_list()

    def add_child(self, child:"DirectoryAsset") -> "DirectoryAsset":
        child.parent_directory = self
        return self.children.setdefault(child.name, child)

    def remove_child() -> None:
        pass
