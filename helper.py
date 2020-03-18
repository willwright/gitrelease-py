import click
import mygit
import os
import re
import subprocess
import yaml


def get_current_release_candidate():
    releases_dict = mygit.config.read_config()

    return "release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"])


def get_next_release_candidate():
    releases_dict = mygit.config.read_config()

    return "release-v{}-rc{}".format(releases_dict["version"], int(releases_dict["candidate"]) + 1)


def release_sort_hash(version, candidate):
    key = 0
    for part in version.split("."):
        key += int(part)*100

    key += int(candidate)

    return key


def get_key(item_dict):
    version = item_dict["version"]
    candidate = item_dict["candidate"]

    return release_sort_hash(version, candidate)


def release_branch_comp(branch):
    branch.replace("remotes/origin/", "")
    key = 0

    regex = re.search("[\d+\.]+\d+", branch)
    version = regex.group()

    regex = re.search("\d+$", branch)
    candidate = regex.group()

    return release_sort_hash(version, candidate)


def find_branch_by_query(query):
    result = subprocess.run(['git', 'branch', '-r'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()
    branches = list(map(lambda x: x.strip(), branches))
    branches = list(filter(lambda x: query.lower() in x.lower(), branches))
    return branches


def use_api_share():
    if not os.path.exists("gitrelease.yaml"):
        return False

    with open("gitrelease.yaml", "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)

    return bool(config_dict["useApiShare"]) or False


def get_current_checkout_branch():
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE)

    return result.stdout.decode('UTF-8')


def parse_jira_key(branch):
    reg_ex = re.search("\/([A-Z])+-\d+", branch)
    jira_key = reg_ex.group().replace("/", "", 1)
    return jira_key


def get_origin_branch_name(branch):
    if branch.lower().startswith("origin/"):
        return branch
    else:
        return "origin/" + branch


def load_configuration():
    script_dir = os.path.expanduser("~/.gitrelease")

    config_dict = {}
    with open(script_dir + "/config.yaml", "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            print(err)
        except:
            print("Error")

    return config_dict


def get_branches_in_release(release_branch):
    pass