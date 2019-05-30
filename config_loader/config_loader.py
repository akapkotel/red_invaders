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
    :return: dicts of lists and dicts -- various game-data in order: player,
    hostiles, powerups, levels, weapons
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

    with open(file, "r") as f:
        unpacked_file = []
        for line in f:
            if line.startswith("#") or line == "\n":
                continue
            else:
                unpacked_file.append(line.strip("\n"))
    return unpacked_file


def convert_unloaded(unpacked_file: list):
    """

    :param unpacked_file:
    :return:
    """
    configs, category, subcategory, data = [], None, None, None
    for line in unpacked_file:
        if line.endswith(":") or line.endswith("EOF"):
            if category is not None: configs.append(locals()[category])
            category = line.strip(":")
            print("Category:", category)
            locals()[category] = {}
        else:
            subcategory = line.split(" = ")[0]
            #print("Subcategory:", subcategory, end=" ")
            data = line.split(" = ")[1]
            if data.startswith("["):  # data is a list
                locals()[category][subcategory] = unpack_list(data)
            elif data.startswith("{"):  # data is a dict
                locals()[category][subcategory] = unpack_dict(data)
            else:
                data_type = get_type(data)  # DATA_TYPES[subcategory]
                locals()[category][subcategory] = data_type(data)
            #print("Value:", locals()[category][subcategory])
    #print(configs)
    return configs


def unpack_list(string_: str):
    """
    Strip, split, translate and unpack provided string to the list.

    :param string_: str -- string to be unpacked into the list
    """
    list_ = []
    string2 = string_.replace("[", "", 1).strip("]")
    elements = string2.split("], ") if "[" in string2 else string2.split(", ")
    for _ in elements:
        if _.startswith("["):
            list_.append(unpack_list(_))
        else:
            list_.append(get_type(_)(_))
    return list_


def unpack_dict(string_: str):
    """
    Recursively strip, split, translate and unpack provided string to the dict.

    :param string_: str -- string to be unpacked into the dict
    """
    dict_ = {}
    string2 = string_.strip("{}")
    elements = string2.split("], ") if "[" in string2 else string2.split(", ")
    for _ in elements:
        #print(_)
        key, value = _.split(": ")[0], _.split(": ")[1]
        if value.startswith("["):
            dict_[key] = unpack_list(value)
        else:
            dict_[key] = get_type(value)(value)
    return dict_


def get_type(string_: str):
    """Find type into which provided string should be casted."""
    if "." in string_ and string_.replace(".", "").isdigit():
        return float
    elif string_.replace("-", "").isdigit():
        return int
    else:
        return str


if __name__ == '__main__':
    print("Is your config_loader in proper directory?")
