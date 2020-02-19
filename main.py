#!/usr/bin/python

import api
from git import Repo
import os
import sh
import subprocess
import sys
import config
from config import incrementCandidate, clearbranches, add
import helper
from jira import parse_jira_key

repo = Repo(os.getcwd())
assert not repo.bare, "This directory is a bare repo, please clone a project to work with"


def jira_sync():
    releases_dict = config.read_config()

    # Get all issues in project/version
    issues_list = api.jira_search_issues(releases_dict["projectslug"], releases_dict["version"])

    # Add any missing branches
    for issue in issues_list:
        for branch in releases_dict["branches"]:
            if helper.key_branch_comp(issue, branch):
                print(issue + " not in branches")

    return


def rm():
    print("Branches found:")
    release_dict = config.read_config()
    for i in range(0, len(release_dict["branches"])):
        print("{}: {}".format(i, release_dict["branches"][i]))

    print("Select a branch to remove: (x = cancel)")
    choice = input() or "x"
    if choice.lower() == "x":
        return
    else:
        choice = int(choice)

    # Remove the FixVersion in JIRA
    print("Send to JIRA [yes]? yes/no")
    jira_send = bool(input()) or "yes"
    if jira_send == "yes":
        jira_send = True
    elif jira_send == "no":
        jira_send = False
    else:
        jira_send = False

    if jira_send:
        jira_key = parse_jira_key(release_dict["branches"][choice])
        api.zapier_delete_fixversion(jira_key, release_dict["version"])

    # Remove the branch from the Dictionary
    del release_dict["branches"][choice]

    # Write the dictionary to git-config
    config.write_config(release_dict)
    # Write the dictionary to DynamoDB
    api.writerelease(release_dict)


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
            api.zapier_create_fixveresion(jira_key, release_dict["version"])

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
        feature_query = input("Enter part of a Feature Branch name: (we will search for it) ").strip()
    elif search_type == 1:
        feature_query = "feature/"
    elif search_type == 2:
        feature_query = "bugfix/"
    elif search_type == 3:
        feature_query = "hotfix/"

    result = subprocess.run(['git', 'branch', '-a'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()
    branches = list(map(lambda x: x.strip(), branches))
    branches = list(filter(lambda x: feature_query.lower() in x.lower(), branches))

    assert len(branches) > 0, "No branches found matching your query"

    for i in range(0, len(branches)):
        print("{option}: {branch}".format(option=i, branch=branches[i]))

    chosen_branch = input("Select Branch (x = cancel): ") or "x"
    if chosen_branch.lower() == "x" or chosen_branch == "":
        return

    chosen_branch = int(chosen_branch)

    print("Selected: {branch}".format(branch=branches[chosen_branch]))
    return branches[chosen_branch]


def init():
    """

    :rtype: object
    """
    release_dict = config.read_config()
    if "projectslug" in release_dict and release_dict["projectslug"]:
        projectslug = input("Choose a projectslug [{}]: ".format(release_dict["projectslug"])) or release_dict["projectslug"]
    else:
        projectslug = input("Choose a projectslug: ")

    release_dict["projectslug"] = projectslug.strip()

    # TODO: Check that the slug and version don't already exist; if they do prompt for confirmation
    #if slugExists(projectslug):
    #    print("That slug already exists")
    #    # TODO: Implement a confirmation here

    release_version = input("Enter Release Version (e.g. 16_07 or 1.0.0): ")
    release_version = release_version.strip()
    assert release_version, "Release Version is required"
    release_dict["version"] = release_version
    release_dict["current"] = "release-v" + release_version

    release_candidate = input("Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1): ") or 0
    release_dict["candidate"] = int(release_candidate)

    status()
    choice = input("Clear branches [yes/no] or inherit from current config? [no]") or "no"
    if choice != "no":
        clearbranches()

    # Write release to config
    config.write_config(release_dict)

    # Write release to API
    api.writerelease(release_dict)


def checkout():
    release_dict = config.read_config()

    print("Checkout")
    if release_dict["projectslug"]:
        projectslug = input("Choose a projectslug [{}]: ".format(release_dict["projectslug"])) or release_dict["projectslug"]
    else:
        projectslug = input("Choose a projectslug: ")

    release_dict["projectslug"] = projectslug.strip()
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
    nextReleaseCandidate = get_next_release_candidate()

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

    merge_branches(branches)

    hasConflicts = find_conflicts()
    if hasConflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        print("git push origin " + nextReleaseCandidate)
        sh.git.push("origin", nextReleaseCandidate)


def next():
    current_release_candidate = get_current_release_candidate()
    nextReleaseCandidate = get_next_release_candidate()

    sh.git.fetch("--all")

    print("Creating " + nextReleaseCandidate + " ...")

    # Change this so that "master" is configurable
    try:
        sh.git.checkout("-b", nextReleaseCandidate, current_release_candidate, _err=sys.stderr)
        incrementCandidate()
        config.write_config()
    except sh.ErrorReturnCode_128:
        sys.exit()

    result = subprocess.run(['git', 'config', '--get-all', 'releases.branches'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()

    merge_branches(branches)

    hasConflicts = find_conflicts()
    if hasConflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        print("git push origin " + nextReleaseCandidate)
        #sh.git.push("origin", nextReleaseCandidate)


def status():
    releases_dict = config.read_config()

    print("Development Branch: {}".format(releases_dict["devbranch"]))
    print("Staging Branch: {}".format(releases_dict["stagebranch"]))
    print()
    print("Branches in this release:")
    for branch in releases_dict["branches"]:
        print(branch)

    return

def merge_branches(branches):
    sh.git.fetch("--all")

    for branch in branches:
        branch = branch.strip()
        print()
        print("Merging: " + branch)
        try:
            sh.git.merge("--no-ff", "--no-edit", branch, _err=sys.stderr, _out=sys.stdout)
        except sh.ErrorReturnCode_1:
            return


def find_conflicts():
    print("Looking for conflicts with merge.")
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], stdout=subprocess.PIPE)
    conflicts = result.stdout.decode('utf-8')

    if conflicts:
        return True
    else:
        return False


def main(argv):
    if len(argv) > 1:
        method = argv[1]+"()"
        exec(method)
    else:
        status()

    return


if __name__ == "__main__":
    main(sys.argv)