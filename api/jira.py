import click
import json
import requests

import utils.configuration


def add_fixveresion(jira_key, version):
    config_dict = utils.configuration.load()

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
                            auth=(config_dict["jira"]["username"], config_dict["jira"]["password"])
                            )
    if response.status_code != 204:
        click.secho("ApiCall Error", fg='red')
        if 'errors' in response.json() and 'fixVersions' in response.json()['errors']:
            click.secho(response.json()['errors']['fixVersions'], fg='red')
        raise Exception

    return


def delete_fixversion(jira_key, version):
    config_dict = utils.configuration.load()

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
                            auth=(config_dict["jira"]["username"], config_dict["jira"]["password"])
                            )
    if response.status_code != 204:
        # Replace this with raise error
        click.secho("ApiCall Error: delete_fixversion", fg='red')
        raise Exception("missing-version")

    return


def search_issues(projectslug, version):
    config_dict = utils.configuration.load()

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
                             auth=(config_dict["jira"]["username"], config_dict["jira"]["password"])
                             )
    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error: search_issues", fg='red')
        if 'errorMessages' in response.json():
            for message in response.json()['errorMessages']:
                click.secho(message, fg='red')
                raise Exception("missing-version")

    issues_list = []
    if "issues" not in response.json():
        return issues_list

    for issue in response.json()["issues"]:
        issues_list.append(issue["key"])

    return issues_list


def create_fixversion(projectslug, version):
    config_dict = utils.configuration.load()

    data = {
        "archived": "false",
        "name": version,
        "project": projectslug
    }

    response = requests.post('https://guidevops.atlassian.net/rest/api/3/version',
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'},
                             auth=(config_dict["jira"]["username"], config_dict["jira"]["password"])
                             )
    if response.status_code != 201:
        # Replace this with raise error
        click.secho("ApiCall Error: create_fixversion", fg='red')
        if 'errorMessages' in response.json():
            for message in response.json()['errorMessages']:
                click.secho(message, fg='red')
            raise Exception('create-fixversion')

    return
