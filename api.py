import json
import requests


def readrproject(release_dict):
    """
    Reads all Release records for the given projectslug
    /project/{project}

    :param release_dict:
    :return:
    """
    projectslug = release_dict["projectslug"]
    version = release_dict["version"]
    response = requests.get("https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/release/{1}".format(projectslug, version))

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if response.json():
        return json.loads(response.json())
    else:
        return {}


def readrelease(release_dict):
    """
    Reads a Release record from the API
    /project/{project}/release/{release}

    :param release_dict:
    :return:
    """
    projectslug = release_dict["projectslug"]
    version = release_dict["version"]
    response = requests.get("https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/release/{1}".format(projectslug, version))

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if response.json():
        return json.loads(response.json())
    else:
        return {}


def writerelease(release_dict):
    """
    Writes a Release record to the API
    /release

    :param release_dict:
    """
    #print()
    #print(json.dumps(releases_dict, indent=4, sort_keys=True))

    response = requests.post('https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/release',
                             data=json.dumps(release_dict),
                             headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")


def slugExists(projectslug):
    response = requests.get('https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{:s}'.format(projectslug))
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if "projectslug" in response.json()["item"]:
        return True
    else:
        return False


