import json
import os
import sys

import requests
import yaml


def create_fixveresion(jira_key, version):
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
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
        print("Issue Added to JIRA successfully")

    return


def delete_fixversion(jira_key, version):
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
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


def search_issues(projectslug, version):
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
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