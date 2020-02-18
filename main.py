#!/usr/bin/python

import git
import api
import config
from git import Repo
import os
import re
import sh
import subprocess
import sys
import config

repo = Repo(os.getcwd())
assert not repo.bare, "This directory is a bare repo, please clone a project to work with"


def add(branch):
    sh.git.config("--add", "releases.branches", branch)


def clearbranches():
    # git config --unset-all releases.branches
    sh.git.config("--local", "--unset-all", "releases.branches")


def feature():
    branch = find_feature()
    if branch:
        add(branch)
        print("Send to JIRA [yes]? yes/no")
        jira_send = bool(input()) or "yes"
        if jira_send == "yes":
            jira_send = True
        elif jira_send == "no":
            jira_send = False
        else:
            jira_send = False

        if jira_send:
            jira_key = parse_jira_key(branch)
            release_dict = config.read_config()
            api.zapier_POST(jira_key, release_dict["version"])

    return

def find_feature():
    print("Find a branch by type, or search for it by name: ")
    print("0 Search by name")
    print("1 List all feature/ branches")
    print("2 List all bugfix/ branches")
    print("3 List all hotfix/ branches")
    search_type = int(input())

    feature_query = ""
    if search_type == 0:
        feature_query = input("Enter part of a Feature Branch name: (we will search for it) ")
    elif search_type == 1:
        feature_query = "feature/"
    elif search_type == 2:
        feature_query = "bugfix/"
    elif search_type == 3:
        feature_query = "hotfix/"

    # TODO: Make sure this is checking remotes as well as locals
    ff_branches = list(filter(lambda x: feature_query in x.name, repo.branches))

    assert len(ff_branches) > 0, "No branches found matching your query"

    option = 0
    for branch in ff_branches:
        print("{option}: {branch}".format(option=option, branch=branch.name))

    chosen_branch = int(input("Select Branch (x = cancel): "))
    if chosen_branch == "x" or chosen_branch == "X" or chosen_branch == "":
        return

    print("Selected: {branch}".format(branch=ff_branches[chosen_branch]))
    return ff_branches[chosen_branch].name


def init():
    """

    :rtype: object
    """
    release_dict = config.read_config()
    projectslug = input("Enter the project slug: ")
    release_dict["projectslug"] = projectslug.strip()

    #if slugExists(projectslug):
    #    print("That slug already exists")
    #    # TODO: Implement a confirmation here

    release_version = input("Enter Release Version (e.g. 16_07 or 1.0.0): ")
    release_version = release_version.strip()
    assert release_version, "Release Version is required"
    release_dict["version"] = release_version
    release_dict["current"] = "release-v" + release_version

    release_candidate = 0
    release_candidate = input("Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1): ")
    release_dict["candidate"] = release_candidate

    #clearbranches()

    # Write release to config
    config.write_config(release_dict)

    # Write release to API
    api.writerelease(release_dict)

def get_key(item_dict):
    key = 0
    for part in item_dict["version"].split("."):
        key += int(part)*100

    key += int(item_dict["candidate"])
    return key


def checkout():
    release_dict = config.read_config()

    print("Checkout")
    if release_dict["projectslug"]:
        projectslug = input("Choose a projectslug [{}]: ".format(release_dict["projectslug"])) or release_dict["projectslug"]
    else:
        projectslug = input("Choose a projectslug: ")

    release_dict["projectslug"] = projectslug
    print()

    # Read all the releases for projectslug
    items_dict = api.readproject(release_dict["projectslug"])
    items_list = sorted(items_dict["Items"], key=get_key, reverse=False)
    for key in range(0, len(items_list)):
        print("{}: release-v{}-rc{}".format(key, items_list[key]["version"], items_list[key]["candidate"]))

    items_list_key = int(input("Choose release: "))
    release_dict = items_list[items_list_key]

    release_dict.pop("projectslug#version#candidate")
    config.write_config(release_dict)

    sh.git.fetch("--all")
    sh.git.checkout("release-v{}-rc{}".format(release_dict["version"], release_dict["candidate"]))


def roll():
    nextReleaseCandidate = getNextReleaseCandidate()

    sh.git.fetch("--all")

    print("Creating " + nextReleaseCandidate + " ...")

    # Change this so that "master" is configurable
    try:
        sh.git.checkout("-b", nextReleaseCandidate, "master", _err=sys.stderr)
        incrementCandidate()
        config.write_config()
    except sh.ErrorReturnCode_128:
        sys.exit()

    result = subprocess.run(['git', 'config', '--get-all', 'releases.branches'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()

    mergeBranches(branches)

    hasConflicts = findConflicts()
    if hasConflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        print("git push origin " + nextReleaseCandidate)
        sh.git.push("origin", nextReleaseCandidate)


def next():
    currentReleaseCandidate = getCurrentReleaseCandidate()
    nextReleaseCandidate = getNextReleaseCandidate()

    sh.git.fetch("--all")

    print("Creating " + nextReleaseCandidate + " ...")

    # Change this so that "master" is configurable
    try:
        sh.git.checkout("-b", nextReleaseCandidate, currentReleaseCandidate, _err=sys.stderr)
        incrementCandidate()
        config.write_config()
    except sh.ErrorReturnCode_128:
        sys.exit()

    result = subprocess.run(['git', 'config', '--get-all', 'releases.branches'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()

    mergeBranches(branches)

    hasConflicts = findConflicts()
    if hasConflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        print("git push origin " + nextReleaseCandidate)
        #sh.git.push("origin", nextReleaseCandidate)


def mergeBranches(branches):
    sh.git.fetch("--all")

    for branch in branches:
        branch = branch.strip()
        print()
        print("Merging: " + branch)
        try:
            sh.git.merge("--no-ff", "--no-edit", branch, _err=sys.stderr, _out=sys.stdout)
        except sh.ErrorReturnCode_1:
            return


def findConflicts():
    print("Looking for conflicts with merge.")
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], stdout=subprocess.PIPE)
    conflicts = result.stdout.decode('utf-8')

    if conflicts:
        return True
    else:
        return False


def incrementCandidate():
    candidate = getCandidate()
    candidate += 1
    sh.git.config("--local", "--replace-all", "releases.candidate", candidate)

def getCurrent():
    return str(sh.git.config("--local", "--get", "releases.current").strip())


def getCandidate():
    return int(sh.git.config("--local", "--get", "releases.candidate").strip())


def getprojectslug():
    return int(sh.git.config("--local", "--get", "releases.projectslug").strip())


def getversion():
    return int(sh.git.config("--local", "--get", "releases.version").strip())


def getCurrentReleaseCandidate():
    current = getCurrent()
    candidate = getCandidate()
    return "{current}-rc{candidate}".format(current=current, candidate=candidate)


def getNextReleaseCandidate():
    current = getCurrent()
    candidate = getCandidate()
    return "{current}-rc{candidate}".format(current=current, candidate=candidate+1)


def parse_jira_key(branch):
    reg_ex = re.search("\/([A-Z])+-\d+", branch)
    jira_key = reg_ex.group().replace("/", "", 1)
    return jira_key

def main(argv):
    method = argv[1]+"()"
    exec(method)


if __name__ == "__main__":
    main(sys.argv)