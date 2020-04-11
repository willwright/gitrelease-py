import click
import json
import requests
from enum import Enum

import utils.configuration

APIGATEWAY_ENDPOINT = "https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/"


class Mode(Enum):
    DEVELOP = "develop"
    PROD = "prod"


def read_project(projectslug):
    """
    Reads all Release records for the given projectslug
    /project/{project}

    :param projectslug:
    :return:
    """
    config_dict = utils.configuration.load()

    endpoint = APIGATEWAY_ENDPOINT + config_dict[utils.configuration.Services.APIGATEWAY.value][
        "mode"] + "/project/{0}"
    response = requests.get(endpoint.format(projectslug),
                            auth=(config_dict[utils.configuration.Services.APIGATEWAY.value]["username"],
                                  config_dict[utils.configuration.Services.APIGATEWAY.value]["password"])
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

    endpoint = APIGATEWAY_ENDPOINT + config_dict[utils.configuration.Services.APIGATEWAY.value][
        "mode"] + "/project/{0}/version/{1}/candidate/{2}"
    response = requests.get(endpoint.format(projectslug, version, candidate),
                            auth=(config_dict[utils.configuration.Services.APIGATEWAY.value]["username"],
                                  config_dict[utils.configuration.Services.APIGATEWAY.value]["password"])
                            )

    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error", fg='red')

    if response.json():
        return response.json()
    else:
        return {}

    pass


def read_candidate_from_parts(projectslug, version, candidate):
    config_dict = utils.configuration.load()

    endpoint = APIGATEWAY_ENDPOINT + config_dict[utils.configuration.Services.APIGATEWAY.value][
        "mode"] + "/project/{0}/version/{1}/candidate/{2}"
    response = requests.get(endpoint.format(projectslug, version, candidate),
                            auth=(config_dict[utils.configuration.Services.APIGATEWAY.value]["username"],
                                  config_dict[utils.configuration.Services.APIGATEWAY.value]["password"])
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

    endpoint = APIGATEWAY_ENDPOINT + config_dict[utils.configuration.Services.APIGATEWAY.value][
        "mode"] + "/release"
    response = requests.post(endpoint,
                             data=json.dumps(release_dict),
                             headers={'Content-Type': 'application/json'},
                             auth=(config_dict[utils.configuration.Services.APIGATEWAY.value]["username"],
                                   config_dict[utils.configuration.Services.APIGATEWAY.value]["password"])
                             )

    if response.status_code != 200:
        # Replace this with raise error
        click.secho("ApiCall Error", fg='red')


def slugExists(projectslug):
    config_dict = utils.configuration.load()

    endpoint = APIGATEWAY_ENDPOINT + config_dict[utils.configuration.Services.APIGATEWAY.value][
        "mode"] + "/project/{:s}"
    response = requests.get(endpoint.format(projectslug),
                            auth=(config_dict[utils.configuration.Services.APIGATEWAY.value]["username"],
                                  config_dict[utils.configuration.Services.APIGATEWAY.value]["password"])
                            )
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if "Items" in response.json() and len(response.json()["Items"]) > 0:
        for item in response.json()["Items"]:
            if "projectslug" in item and item["projectslug"] == projectslug:
                return True

    return False


def enabled():
    config_dict = utils.configuration.load()
    if not utils.configuration.hasService(utils.configuration.Services.APIGATEWAY) or "enabled" not in config_dict[
        utils.configuration.Services.APIGATEWAY.value]:
        return False

    if config_dict[utils.configuration.Services.APIGATEWAY.value]["enabled"] == "y":
        return True
    else:
        return False
