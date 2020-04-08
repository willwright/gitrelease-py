import json

import click
import requests

import utils.configuration


def read_project(projectslug):
    """
    Reads all Release records for the given projectslug
    /project/{project}

    :param projectslug:
    :return:
    """
    config_dict = utils.configuration.load()
    response = requests.get(
        "https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}".format(projectslug),
        auth=(config_dict["apigateway"]["username"], config_dict["apigateway"]["password"])
    )

    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error", fg='red')

    if response.json():
        return response.json()
    else:
        return {}


def read_candidate(release_dict):
    config_dict = utils.configuration.load()

    projectslug = release_dict["projectslug"]
    version = release_dict["version"]
    candidate = release_dict["candidate"]
    response = requests.get(
        "https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/version/{1}/candidate/{2}".format(
            projectslug, version, candidate),
        auth=(config_dict["apigateway"]["username"], config_dict["apigateway"]["password"])
    )

    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error", fg='red')

    if response.json():
        return response.json()
    else:
        return {}

    pass


def read_candidate(projectslug, version, candidate):
    config_dict = utils.configuration.load()

    response = requests.get(
        "https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/version/{1}/candidate/{2}".format(
            projectslug, version, candidate),
        auth=(config_dict["apigateway"]["username"], config_dict["apigateway"]["password"])
    )

    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error", fg='red')

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
    config_dict = utils.configuration.load()

    response = requests.post('https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/release',
                             data=json.dumps(release_dict),
                             headers={'Content-Type': 'application/json'},
                             auth=(config_dict["apigateway"]["username"], config_dict["apigateway"]["password"])
                             )

    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error", fg='red')


def slugExists(projectslug):
    config_dict = utils.configuration.load()
    response = requests.get(
        'https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{:s}'.format(projectslug),
        auth=(config_dict["apigateway"]["username"], config_dict["apigateway"]["password"])
    )
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if "Items" in response.json() and len(response.json()["Items"]) > 0:
        for item in response.json()["Items"]:
            if "projectslug" in item and item["projectslug"] == projectslug:
                return True

    return False


def enabled() -> bool:
    config_dict = utils.configuration.load()
    if not utils.configuration.hasService(utils.configuration.Services.APIGATEWAY) or "enabled" not in config_dict[
        utils.configuration.Services.APIGATEWAY.value]:
        return False

    if config_dict[utils.configuration.Services.APIGATEWAY.value]["enabled"] == "y":
        return True
    else:
        return False
