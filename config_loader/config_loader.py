import os


def load_config_from_file(path: str, file: str):
    """
    Find, open and unpack data from config txt file into the internal data
    structures. Config file should be located in the 'config_files' directory.
    Config file must be structured accordingly to the rules - see 'README.txt'
    in config directory,
    Data retrieved from files is processed to the lists and dicts, which are
    later used by object constructors in the classes and by methods of the
    Game class.

    :param path: str -- absolute path to the config file, for testing provide
    path to the test config files
    :param file: str -- name of the config file
    :return: dicts of lists and dicts -- various game-data in the same order
    you ordered your txt file
    """
    os.chdir(path)
    unloaded = file_unload(file)
    return convert_unloaded(unloaded)


def file_unload(file: str):
    """
    Open text file, read it's contents and write unpack them into list.

    :param file: str -- name of the config file
    :return: list -- list of lines read from the file
    """
    unpacked_file = []
    with open(file, "r") as f:
        for line in f:
            if line.startswith("#") or line == "\n":
                continue
            else:
                unpacked_file.append(line.strip("\n"))
    return unpacked_file


def convert_unloaded(unpacked_file: list):
    """
    Read lines extracted from config file one by one, identify them, set the
    categories, subcategories, and transform strings to the correct data types
    required by internal data structures.

    :param unpacked_file: list -- list of strings unpacked from file
    :return: list of dicts and lists -- structured data in strict order from
    the config file
    """
    configs, category, subcategory, data = [], None, None, None
    for line in unpacked_file:
        if line.endswith(":") or line.endswith("EOF"):
            if category is not None: configs.append(locals()[category])
            category = line.strip(":")
            locals()[category] = {}
        else:
            subcategory = line.split(" = ")[0]
            data = line.split(" = ")[1]
            if data.startswith("["):  # data is a list
                locals()[category][subcategory] = unpack_list(data)
            elif data.startswith("{"):  # data is a dict
                locals()[category][subcategory] = unpack_dict(data)
            else:
                data_type = get_type(data)
                locals()[category][subcategory] = data_type(data)
    return configs


def unpack_list(string_: str):
    """
    Recursively strip, split, translate and unpack provided string to the list.

    :param string_: str -- string to be unpacked into the list
    :return: list
    """
    list_ = []
    string2 = string_.replace("[", "", 1).strip("]")
    elements = string2.split("], ") if "[" in string2 else string2.split(", ")
    for i in elements:
        if i.startswith("["):
            list_.append(unpack_list(i))
        elif i.startswith("{"):
            list_.append(unpack_dict(i))
        else:
            list_.append(get_type(i)(i))
    return list_


def unpack_dict(string_: str):
    """
    Recursively strip, split, translate and unpack provided string to the dict.

    :param string_: str -- string to be unpacked into the dict
    :return: dict
    """
    dict_ = {}
    string2 = string_.strip("{}")
    elements = string2.split("], ") if "[" in string2 else string2.split(", ")
    for i in elements:
        key, value = i.split(": ")[0], i.split(": ")[1]
        if value.startswith("["):
            dict_[key] = unpack_list(value)
        elif value.startswith("{"):
            dict_[key] = unpack_dict(value)
        else:
            dict_[key] = get_type(value)(value)
    return dict_


def get_type(string_: str):
    """
    Find type into which provided string should be casted.

    :param string_: str -- single string to reformat
    :return: float, int, bool or str
    """
    if "." in string_ and string_.replace(".", "").isdigit():
        return float
    elif string_.replace("-", "").isdigit():
        return int
    elif string_ in ("True", "False"):
        return bool
    else:
        return str


if __name__ == '__main__':
    print("Is your config_loader in proper directory?")
