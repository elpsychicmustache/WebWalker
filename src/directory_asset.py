from pathlib import Path

class DirectoryAsset():
    master_list = []


    def __init__(self, name:str, level:int, parent:"DirectoryAsset"=None, children:dict[str, "DirectoryAsset"]=None) -> None:
        """Create a DirectoryAsset object, which represents a directory with a possible parent or children nodes.

        To prevent recursion, a DirectoryAsset should only have one parent node. Any instantiated DirectoryAsset will be added to the
        master_list class variable to prevent duplicate directories from appearing (again, to prevent recursion).
        If this is the first DirectoryAsset object, it is recommended to start with level=2.

        :param name: The directory name.
        :type name: str
        :param level: The hierarchy level of a directory. Children will be appended with level+=2
        :type level: int
        :param parent: The parent DirectoryAsset.
        :type parent: DirectoryAsset
        :param children: A dictionary containing the child's name, and the child DirectoryAsset object.
        :type children: dict[str, DirectoryAsset]
        """
        self.name = name
        self.level = level
        self.parent = parent
        self.children = children or {}

        DirectoryAsset.master_list.append(self)  # keeping track of a master list to prevent recursive entries

    def populate_directories(self, directory_string_list:str) -> None:
        """Populate children directories.

        The way children directories are bulk populated is by running walkman.js, and saving the results as a text file.
        This method handles the list as a string, drops malformed entries, and splits each entry into a DirectoryAsset
        with self as the parent.

        :param directory_string_list: The results from walkman.js as a text file.
        :type directory_string_list: str like list
        """
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
            # The following two lines are needed in case the directory exists as a child (or parent) somewhere else.
            elif directory in [x.name for x in DirectoryAsset.master_list]:
                continue
            else:
                directories_to_add.add(directory)

        for directory in directories_to_add:
            child_directory = DirectoryAsset(directory, level=self.level+2, parent=self)
            self.add_child(child_directory)  # this creates the dictionary entry for children

    def add_child(self, child:"DirectoryAsset"=None) -> "DirectoryAsset":
        """Add a single child to self.

        Currently, this will only accept a DirectoryAsset. In future iterations, I plan
        to allow an empty child, and allow the user to interactively add a child directory.

        :param child: The DirectoryAsset to as a child to self. Defaults to None.
        :type child: DirectoryAsset
        """
        # TODO: child=None should be handled differently; i.e. interactively created
        child.parent_directory = self

        self.children.setdefault(child.name, child)  # adding child as directory
        self.sort_children()  # sort children based by alphabetical order

    def sort_children(self) -> None:
        """Sorts children directories by alphabetical order."""
        self.children = dict(sorted(self.children.items()))

    def print_asset_list(self, file_name:"PosixPath"=None) -> None:
        """Print the directory tree from the perspective of self.

        I am currently researching how to do curses. Hence, future iteration should probably
        return this as a string instead of printing directly to stdout.
        """
        # The following two lines are needed to prevent double printing of directory names
        # between child and parent. However, this has the unintended consequence of
        # not printing self.name if self is a child to a DirectoryAsset.
        if not self.parent:
            print("- " + self.name, file=file_name)
        if not self.children:
            print(f"[!] No subdirectories found for {self.name}", file=file_name)
            return  # exit the function

        for directory in self.children.keys():
            print(" " * self.level, end="", file=file_name)
            print("- " + directory, file=file_name)
            if self.children[directory].children:
                self.children[directory].print_asset_list(file_name=file_name)

    def get_asset_list(self) -> list[str]:
        """Returns a string list version of print_asset_list

        :returns: A list containing the names of the directory assets.
        :rtype: list[str]
        """
        asset_list = []

        if not self.children:
            raise IndexError(f"[!] No subdirectories found for {self.name}")
        if not self.parent:
            asset_list.append("- " + self.name)
        for directory in self.children.keys():
            asset_list.append(" "*self.level + "- " + directory)
            if self.children[directory].children:
                asset_list = asset_list + self.children[directory].get_asset_list()

        return asset_list

    def populate_child_directories(self, child_directory_name:str, input_file_name:str) -> None:
        """Running this method allows the user to populate children directores from a directly linked child node.

        The benefit of this is being able to populate children directories,
        without having to switch to the child itself.
        """

        data_path = Path(__file__).resolve().parent.parent / "data" / input_file_name

        with open(data_path, "r") as file:
            directories = file.read().strip()

        self.children[child_directory_name].populate_directories(directories)

    def remove_child(self) -> None:
        """Remove a child directory.

        Not currently implemented. Running this does nothing.
        """
        pass

    def create_output_file(self, output_file_name:str="output.txt") -> None:
        data_path = Path(__file__).parent.parent.resolve()
        data_path = data_path / "data" / output_file_name
        self.print_asset_list(file_name=data_path)
