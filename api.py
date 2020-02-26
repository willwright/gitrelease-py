import json
import os
import requests
import yaml


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


def readversion(release_dict):
    pass


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


def jira_create_fixveresion(jira_key, version):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(script_dir + "/config.yaml", "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)
        except:
            print("Error")

    data = {
        "update": {
            "fixVersions": [
                {
                    "add": {
                        "name": "{}".format(version)
                    }
                }
            ]
        }
    }
    response = requests.put('https://guidevops.atlassian.net/rest/api/3/issue/{}'.format(jira_key),
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                            auth=(config_dict["username"], config_dict["password"])
                            )
    if response.status_code != 204:
        # Replace this with raise error
        print("ApiCall Error")
    else:
        print("Issue Removed from JIRA successfully")

    return


def jira_delete_fixversion(jira_key, version):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(script_dir + "/config.yaml", "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)
        except:
            print("Error")

    data = {
        "update": {
            "fixVersions": [
                {
                    "remove": {
                        "name": "{}".format(version)
                    }
                }
            ]
        }
    }
    response = requests.put('https://guidevops.atlassian.net/rest/api/3/issue/{}'.format(jira_key),
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                            auth=(config_dict["username"], config_dict["password"])
                            )
    if response.status_code != 204:
        # Replace this with raise error
        print("ApiCall Error")
    else:
        print("Issue Removed from JIRA successfully")

    return


def jira_search_issues(projectslug, version):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(script_dir + "/config.yaml", "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)

    data = {
        "expand": [],
        "jql": "project = {} AND fixVersion in ({})".format(projectslug, version),
        "fieldsByKeys": False,
        "fields": [],
        "startAt": 0
    }

    response = requests.post('https://guidevops.atlassian.net/rest/api/3/search',
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'},
                             auth=(config_dict["username"], config_dict["password"])
                             )
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    issues_list = []
    for issue in response.json()["issues"]:
        issues_list.append(issue["key"])

    return issues_list
