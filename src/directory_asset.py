from pathlib import Path
from urllib.parse import urlparse


def strip_hostname(path: str, hostname:str) -> str:
    """Remove scheme://hostname from URLs and return only the path."""
    #try:
    parsed = urlparse(path)
    # If it's a valid absolute URL (http/https), keep only the path
    if parsed.scheme in ("http", "https") and parsed.netloc == hostname:
        clean = parsed.path
        if not clean.startswith("/"):
            clean = "/" + clean
        return clean or path
    else:
        return path
    #except:
        #return path

    #return path


def get_datafile(input_file:str) -> str:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    input_file = project_root / "data" / input_file

    with open(input_file, "r") as file:
        directories = file.read().strip()

    return directories


class DirectoryAsset():
    master_list:list = []
    hostname:str = None


    def __init__(self, name:str, level:int=2, parent:"DirectoryAsset"=None, children:dict[str, "DirectoryAsset"]=None) -> None:
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
        # Checking if the directory already exists. If so, raise an error.
        try:
            directory_index = [directory.name for directory in DirectoryAsset.master_list].index(name)
        except ValueError:
            pass
        else:
            # If the parent has a name, then show it. Otherwise, just tell user the directory already exists.
            if DirectoryAsset.master_list[directory_index].parent:
                raise ValueError(f"[!] Cannot create {name} - it already exists as a parent to {DirectoryAsset.master_list[directory_index].parent.name}")
            else:
                raise ValueError(f"[!] Cannot create {name} - it already exists as a directory.")

        self.name = name
        self.level = level
        self.parent = parent
        self.children = children or {}  # children should be like so {child.name, object}

        DirectoryAsset.master_list.append(self)  # keeping track of a master list to prevent recursive entries


    def populate_directories(self, directory_string_list:str) -> None:
        """Populate children directories.

        The way children directories are bulk populated is by running walkman.js, and saving the results as a text file.
        This method handles the list as a string, drops malformed entries, and splits each entry into a DirectoryAsset
        with self as the parent.

        :param directory_string_list: The results from walkman.js as a text file.
        :type directory_string_list: str like list
        """
        # Removing specific characters from directory_string_list so that it can be parsed correctly.
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
            cleaned = strip_hostname(directory, DirectoryAsset.hostname)

            if cleaned == self.name:
                continue
            elif "#" in cleaned:
                continue
            elif cleaned in [x.name for x in DirectoryAsset.master_list]:
                continue
            else:
                directories_to_add.add(cleaned)

        for directory in directories_to_add:
            # Ignore ValueErrors raised by object creation if the directory already exists.
            # Removing the try/except block will cause errors when trying to bulk add entries.
            try:
                child_directory = DirectoryAsset(name=directory, level=self.level+2, parent=self)
            except ValueError:
                pass
            else:
                self.add_child(child_directory)  # this creates the dictionary entry for children

    def add_child(self, child:"DirectoryAsset"=None) -> None:
        """Add a single child to self.

        :param child: The DirectoryAsset to as a child to self. Defaults to None.
        :type child: DirectoryAsset
        """

        child.parent_directory = self

        self.children.setdefault(child.name, child)  # adding child as directory
        self.sort_children()  # sort children based by alphabetical order

    def sort_children(self) -> None:
        """Sorts children directories by alphabetical order."""
        self.children = dict(sorted(self.children.items()))

    def get_asset_list_string(self) -> str:
        """Return the directory tree as a string from the perspective of self.

        :returns: The directory tree as a string.
        :rtype: str
        """

        # The following two lines are needed to prevent double printing of directory names
        # between child and parent. However, this has the unintended consequence of
        # not printing self.name if self is a child to a DirectoryAsset.
        return_string = ""

        if not self.parent:
            return_string += "- " + self.name + "\n"
            # print("- " + self.name)
        if not self.children:
            return_string += f"No subdirectories found for {self.name}"
            # print(f"[!] No subdirectories found for {self.name}")
            return  # exit the function

        for directory in self.children.keys():
            return_string += " " * self.level
            # print(" " * self.level, end="")
            return_string += "- " + directory + "\n"
            # print("- " + directory)
            if self.children[directory].children:
                return_string += self.children[directory].get_asset_list_string()

        return return_string

    def get_asset_list(self) -> list[str]:
        """Returns a list version of get_asset_list_string()

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

        :param child_directory_name: The name of the child directory.
        :type child_directory_name: str
        :param input_file_name: The name of the input file in ../data/
        :type input_file_name: str
        """

        data_path = Path(__file__).resolve().parent.parent / "data" / input_file_name

        with open(data_path, "r") as file:
            directories = file.read().strip()

        self.children[child_directory_name].populate_directories(directories)

    def remove_child(self, child_name:str) -> None:
        """Remove a child directory.

        Not currently implemented. Running this does nothing.
        """
        # Figure out if child exists.
        try:
            self.children[child_name]
        except KeyError:
            raise ValueError(f"[!] {child_name} is not a valid child directory.")
            return  # end this function call

        # Remove the child from the children list.
        directory_object = self.children.pop(child_name)
        # Remove the child from the master list.
        DirectoryAsset.master_list.remove(directory_object)
        # Attempt to delete the child.
        del directory_object

    def create_output_file(self, output_file_name:str="output.txt") -> None:
        """Create an output file of the directory tree.

        Currently, this saves the data as the string generated from get_asset_list_string().

        :param output_file_name: The name of the file to save to. DEFAULTS to output.txt
        :type output_file_name: str
        """
        data_path = Path(__file__).parent.parent.resolve()
        data_path = data_path / "data" / output_file_name
        asset_list_string = self.get_asset_list_string()

        data_path.write_text(asset_list_string)
