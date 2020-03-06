import json
import requests


def read_project(projectslug):
    """
    Reads all Release records for the given projectslug
    /project/{project}

    :param projectslug:
    :return:
    """
    response = requests.get(
        "https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}".format(projectslug))

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if response.json():
        return response.json()
    else:
        return {}


def read_candidate(release_dict):
    projectslug = release_dict["projectslug"]
    version = release_dict["version"]
    candidate = release_dict["candidate"]
    response = requests.get(
        "https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/version/{1}/candidate/{2}".format(
            projectslug, version, candidate))

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if response.json():
        return response.json()
    else:
        return {}

    pass


def writerelease(release_dict):
    """
    Writes a Release record to the API
    /release

    :param release_dict:
    """
    # print()
    # print(json.dumps(releases_dict, indent=4, sort_keys=True))

    response = requests.post('https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/release',
                             data=json.dumps(release_dict),
                             headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")


def slugExists(projectslug):
    response = requests.get(
        'https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{:s}'.format(projectslug))
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if "projectslug" in response.json()["item"]:
        return True
    else:
        return False