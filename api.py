import json
import requests


def readproject(projectslug):
    """
    Reads all Release records for the given projectslug
    /project/{project}

    :param projectslug:
    :return:
    """
    response = requests.get("https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}".format(projectslug))

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
    response = requests.get("https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/version/{1}/candidate/{2}".format(projectslug, version, candidate))

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


def zapier_create_fixveresion(jira_key, version):
    data = {
        "issue_key": jira_key,
        "version": version

    }
    response = requests.post('https://hooks.zapier.com/hooks/catch/728485/odvoq2i/',
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'}
                            )
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    return


def zapier_delete_fixversion(jira_key, version):
    data = {
        "issue_key": jira_key,
        "version": version

    }
    response = requests.put('https://hooks.zapier.com/hooks/catch/728485/omo93b1/',
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'}
                            )
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    return


def jira_search_issues(projectslug, version):
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
                             auth=('wwrig@guidance.com', 'wgpIT65Wqb8fBuiLW4Q3E57F')
                             )
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    issues_list = []
    for issue in response.json()["issues"]:
        issues_list.append(issue["key"])

    return issues_list
