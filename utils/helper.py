import re
import subprocess
import sys

import click
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


def find_conflicts():
    print()
    print("Looking for conflicts with merge.")
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], stdout=subprocess.PIPE)
    conflicts = result.stdout.decode('utf-8')

    if conflicts:
        return True
    else:
        return False


def find_feature(needle):
    if needle:
        feature_query = needle
    else:
        print("Find a branch by type, or search for it by name")
        print("0: Search by name")
        print("1: List all feature/ branches")
        print("2: List all bugfix/ branches")
        print("3: List all hotfix/ branches")

        search_type = click.prompt("Search by", type=click.IntRange(0, 3), default=0)

        feature_query = ""
        if search_type == 0:
            feature_query = click.prompt("Enter part of a Feature Branch name (we will search for it)",
                                         type=str).strip()
        elif search_type == 1:
            feature_query = "feature/"
        elif search_type == 2:
            feature_query = "bugfix/"
        elif search_type == 3:
            feature_query = "hotfix/"
        else:
            return

    branches = find_branch_by_query(feature_query)

    if len(branches) <= 0:
        click.secho("No branches found", fg='red')
        return

    for i in range(0, len(branches)):
        print("{option}: {branch}".format(option=i, branch=branches[i]))

    # If there is only one branch in the list to show, default the prompt to that branch
    if len(branches) == 1:
        default = 0
    else:
        default = "x"

    choice = click.prompt("Select branch (x = cancel)", type=str, default=default)
    try:
        choice = int(choice)
    except:
        return

    print("Selected: {branch}".format(branch=branches[choice]))

    return branches[choice].replace("remotes/", "", 1)


def merge_branches(branches):
    # sh.git.fetch("--all")
    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)

    for branch in branches:
        branch = branch.strip()
        print()
        print("Merging: " + branch)
        try:
            # sh.git.merge("--no-ff", "--no-edit", branch, _err=sys.stderr, _out=sys.stdout)
            subprocess.run(["git", "merge", "--no-ff", "--no-edit", branch], stdout=sys.stdout, stderr=sys.stderr)

        except:
            continue
    return


def show_status():
    releases_dict = mygit.config.read_config()

    click.echo("Master Branch: {}".format(releases_dict["masterbranch"] if "masterbranch" in releases_dict else "None"))
    click.echo("Staging Branch: {}".format(releases_dict["stagebranch"] if "stagebranch" in releases_dict else "None"))
    click.echo("Development Branch: {}".format(releases_dict["devbranch"] if "devbranch" in releases_dict else "None"))
    click.echo("Checked out Branch: {}".format(get_current_checkout_branch()))
    click.echo("----------------------------------------------")
    click.echo("Current Version: {}".format(releases_dict["version"]))
    click.echo("Current Candidate: {}".format(releases_dict["candidate"]))
    click.echo()
    click.echo("Branches in this release:")
    for branch in releases_dict["branches"]:
        click.echo(branch)

    return
