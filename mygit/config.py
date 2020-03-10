import subprocess


def read_config():
    """
    Reads the "releases" section from mygit config and returns a dictionary
    :rtype: dictionary
    :return:
    """
    result = subprocess.run(['git', 'config', '--local', '--get-regex', 'releases'], stdout=subprocess.PIPE)
    releases_list = result.stdout.decode('utf-8')
    releases_list = releases_list.splitlines()

    #print(type(releasesList))
    #print(releasesList)

    releases_list = list(map(lambda x: x.split(" "), releases_list))
    #print()
    #print(type(releasesList))
    #print(releasesList)

    releases_dict = {"branches": []}
    for item in releases_list:
        if item[0] == "releases.branches":
            # TODO: Add de-dupe function
            releases_dict["branches"].append(item[1])
        else:
            releases_dict[item[0].replace("releases.", "")] = item[1]

    return releases_dict


def write_config(release_dict):
    """
    Writes the given dictionary to mygit config "releases" section
    :param release_dict:
    :return:
    """
    for item in release_dict:
        if item == "branches":
            subprocess.run(['git', 'config', '--local', '--unset-all', 'releases.branches'])
            for branch in release_dict["branches"]:
                subprocess.run(['git', 'config', '--local', '--add', 'releases.branches', branch])
            pass
        else:
            subprocess.run(['git', 'config', '--local', 'releases.{0}'.format(item), str(release_dict[item])])

    return

