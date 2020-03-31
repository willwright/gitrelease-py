import re
import subprocess

import os
import yaml

import mygit


def get_current_release_candidate():
    releases_dict = mygit.config.read_config()

    return "release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"])


def get_next_release_candidate():
    releases_dict = mygit.config.read_config()

    return "release-v{}-rc{}".format(releases_dict["version"], int(releases_dict["candidate"]) + 1)


def most_digits(branch_list):
    retval = 0

    for branch in branch_list:
        branch.replace("remotes/origin/", "")

        regex = re.search("[\d+\.]+\d+", branch)
        version = regex.group()

        regex = re.search("\d+$", branch)
        candidate = regex.group()

        item = version.replace(".", "")

        if len(item) > retval:
            retval = len(item)

    return retval


def release_branch_comp(branch, length):
    branch.replace("remotes/origin/", "")
    key = 0

    regex = re.search("[\d+\.]+\d+", branch)
    version = str(regex.group())

    version = version.replace(".", "")
    version = version.ljust(length, "0")

    regex = re.search("\d+$", branch)
    candidate = str(regex.group())

    retval = version + candidate

    return int(retval)


def sort_branches(branches_list):
    max_digits = most_digits(branches_list)

    sorted = False
    while not sorted:
        for i in range(0, len(branches_list) - 2):
            current = release_branch_comp(branches_list[i], max_digits)
            next = release_branch_comp(branches_list[i + 1], max_digits)
            if current > next:
                branches_list[i] = next
                branches_list[i + 1] = current
                sorted = False
                continue

            sorted = True

    return branches_list


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
