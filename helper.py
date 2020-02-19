import config
import jira
import re

def get_current_release_candidate():
    releases_dict = config.read_config()

    return "release-v{}-rc{candidate}".format(releases_dict["version"], releases_dict["candidate"])


def get_next_release_candidate():
    releases_dict = config.read_config()

    return "release-v{}-rc{candidate}".format(releases_dict["version"], int(releases_dict["candidate"]) + 1)


def get_key(item_dict):
    key = 0
    for part in item_dict["version"].split("."):
        key += int(part)*100

    key += int(item_dict["candidate"])
    return key


def key_branch_comp(key, branch):
    key_part = re.search("\d+", key).group()
    branch_part = jira.parse_jira_key(branch)
    branch_part = re.search("\d+", branch_part).group()

    return key_part in branch_part
