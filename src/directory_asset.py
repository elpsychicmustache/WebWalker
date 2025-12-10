from pathlib import Path
from urllib.parse import urlparse


def parse_url_info(path: str) -> str:
    """Parse url information and return the information in separate information."""
    parsed = urlparse(path)

    return (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)

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

    def nuke_directory():
        """This function call nukes the entire DirectoryAsset's existing directory tree.

        Currently, the only thing that needs to happen is clear master_list, but there may
        be other things needed in the future that this method can use.
        """
        DirectoryAsset.master_list = []


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

        self.name = name  # the full URL
        self.level = level
        self.parent = parent
        self.children = children or {}  # children should be like so {child.name, object}

        # urllib parsed information
        self.scheme:str = None
        self.netloc:str = None
        self.path:str = None
        self.params:str = None
        self.query:str = None
        self.fragment:str = None

        self.scheme, self.netloc, self.path, self.params, self.query, self.fragment = parse_url_info(self.name)

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

            if directory == self.name:
                continue
            elif "#" in directory:
                continue
            elif directory in [x.name for x in DirectoryAsset.master_list]:
                continue
            else:
                directories_to_add.add(directory)

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

    def get_asset_list_string(self, first_call=True) -> str:
        """Return the directory tree as a string from the perspective of self.

        :param first_call: Used to prevent double printing of name attributes. Recommended to not touch this. DEFAULTS to true.
        :type first_call: bool
        :returns: The directory tree as a string.
        :rtype: str
        """

        return_string = ""

        if not self.children:
            raise IndexError(f"[!] No subdirectories found for {self.name}")
        if first_call:
            return_string += "- " + self.name + "\n"

        for directory in self.children.keys():
            return_string += " " * self.level
            return_string += "- " + directory + "\n"
            if self.children[directory].children:
                return_string += self.children[directory].get_asset_list_string(first_call=False)

        return return_string

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

    def get_asset_details(self) -> str:
        return_string = ""
        return_string += f"Name: {self.name}\n"
        if self.parent:
            return_string += f"Parent: {self.parent.name}\n"
        return_string += f"Number of children: {len(self.children)}\n"

        if self.scheme:
            return_string += f"\nScheme: {self.scheme}"
        if self.netloc:
            return_string += f"\nNetloc: {self.netloc}"
        if self.path:
            return_string += f"\nPath: {self.path}"
        if self.params:
            return_string += f"\nParams: {self.params}"
        if self.query:
            return_string += f"\nQuery: {self.query}"
        if self.fragment:
            return_string += f"\nFragment: {self.fragment}"

        return return_string
