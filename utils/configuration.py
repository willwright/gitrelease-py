import os
import yaml
from enum import Enum

CONFIG_DIR = ".gitrelease"
CONFIG_FILE = "config.yaml"


class Services(Enum):
    JIRA = "jira"
    GITHUB = "github"
    APIGATEWAY = "apigateway"


def load():
    script_dir = os.path.expanduser("~/" + CONFIG_DIR)

    config_dict = {}
    with open(script_dir + "/" + CONFIG_FILE, "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)
        except:
            print("Error")

    return config_dict


def save(config_dict):
    script_dir = os.path.expanduser("~/" + CONFIG_DIR)

    with open(script_dir + "/" + CONFIG_FILE, "w") as stream:
        try:
            yaml.dump(config_dict, stream, )
        except yaml.YAMLError as err:
            print(err)
        except Exception as err:
            print(err)

    return config_dict


def hasService(service) -> bool:
    config_dict_read = load()
    if service.value in config_dict_read:
        return True
    else:
        return False
