#!/usr/bin/python

import api
import config
from git import Repo
import helper
import local
import jira
import os
import sh
import subprocess
import sys

repo = Repo(os.getcwd())
assert not repo.bare, "This directory is a bare repo, please clone a project to work with"


def jira_sync_down():
    releases_dict = config.read_config()

    # Get all issues in project/version
    issues_list = api.jira_search_issues(releases_dict["projectslug"], releases_dict["version"])

    # Add any missing branches
    for issue in issues_list:
        found = False
        for branch in releases_dict["branches"]:
            if issue in branch:
                print("{}: found!".format(issue))
                found = True

        if not found:
            print("{} is missing!".format(issue))
            print()
            print("0: Add to local release")
            print("1: Remove from JIRA release")
            print("2: Skip")
            choice = input("Selection: [0]".format(issue)) or 0
            print()

            if int(choice) == 0:
                branches = helper.find_branch_by_query(issue)
                if len(branches) <0:
                    print("No branches found matching your query")
                    print()
                    continue

                for i in range(0, len(branches)):
                    print("{option}: {branch}".format(option=i, branch=branches[i]))

                chosen_branch = input("Select Branch (x = cancel): ") or "x"
                if chosen_branch.lower() == "x" or chosen_branch == "":
                    print()
                    continue

                chosen_branch = int(chosen_branch)

                print("Selected: {branch}".format(branch=branches[chosen_branch]))
                print()
                releases_dict["branches"].append(branches[chosen_branch])

            elif int(choice) == 1:
                api.jira_delete_fixversion(issue, releases_dict["version"])
                print("Removed {} from {}".format(issue, releases_dict["version"]))
                print()
            elif int(choice) == 2:
                continue
            else:
                continue

    config.write_config(releases_dict)
    return


def jira_sync_up():
    releases_dict = config.read_config()

    # Get all issues in project/version
    issues_list = api.jira_search_issues(releases_dict["projectslug"], releases_dict["version"])

    # Add any missing branches
    for branch in releases_dict["branches"]:
        found = False
        for issue in issues_list:
            if jira.parse_jira_key(branch) in issue:
                print("{}: found!".format(branch))
                found = True
        if not found:
            print("{} is missing!".format(branch))
            print()
            print("0: Add to JIRA release")
            print("1: Remove from local release")
            print("2: Skip")
            choice = input("Selection: [0]".format(branch)) or 0
            print()
            if int(choice) == 0:
                api.jira_create_fixveresion(jira.parse_jira_key(branch), releases_dict["version"])
            elif int(choice) == 1:
                releases_dict["branches"].remove(branch)
                continue
            elif int(choice) == 2:
                continue
            else:
                continue
    config.write_config(releases_dict)
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
        jira_key = jira.parse_jira_key(release_dict["branches"][choice])
        api.jira_delete_fixversion(jira_key, release_dict["version"])

    # Remove the branch from the Dictionary
    del release_dict["branches"][choice]

    # Write the dictionary to git-config
    config.write_config(release_dict)
    # Write the dictionary to DynamoDB
    api.writerelease(release_dict)


def feature():
    branch = find_feature()
    if branch:
        config.add(branch)
        print("Send to JIRA [yes]? yes/no")
        jira_send = bool(input()) or "yes"
        if jira_send == "yes":
            jira_send = True
        elif jira_send == "no":
            jira_send = False
        else:
            jira_send = False

        if jira_send:
            jira_key = jira.parse_jira_key(branch)
            release_dict = config.read_config()
            api.jira_create_fixveresion(jira_key, release_dict["version"])

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

    branches = helper.find_branch_by_query(feature_query)

    assert len(branches) > 0, "No branches found matching your query"

    for i in range(0, len(branches)):
        print("{option}: {branch}".format(option=i, branch=branches[i]))

    chosen_branch = input("Select Branch (x = cancel): ") or "x"
    if chosen_branch.lower() == "x" or chosen_branch == "":
        return

    chosen_branch = int(chosen_branch)

    print("Selected: {branch}".format(branch=branches[chosen_branch]))
    return branches[chosen_branch].replace("remotes/", "", 1)


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
        config.clearbranches()

    # Write release to config
    config.write_config(release_dict)

    # Write release to API
    api.writerelease(release_dict)


def checkout():
    release_dict = config.read_config()

    sh.git.fetch("--all")
    print("Getting Release Branches...")
    branches_list = helper.find_branch_by_query("origin/release-v")

    if len(branches_list) <= 0:
        print("No Release Branches found in repo")

    # Remove "remotes/" from the beginning of the branch name
    branches_list = map(lambda x: x.replace("remotes/", "", 1), branches_list)

    # Sort the branches by version, candidate
    branches_list = sorted(branches_list, key=helper.release_branch_comp, reverse=False)
    for key in range(0, len(branches_list)):
        print("{}: {}".format(key, branches_list[key]))

    choice = input("Choose release (x = cancel): ") or "x"
    if choice.strip().lower() == "x":
        return
    else:
        choice = int(choice)

    choice_branch = branches_list[choice]
    sh.git.checkout(choice_branch.replace("origin/", "", 1))

    # TODO: Update release_dict branches from one of these two sources
    if helper.use_api_share():
        # Update release_dict from the API
        raw_candidate = api.read_candidate(release_dict)
        if "Item" in raw_candidate:
            release_dict = raw_candidate["Item"]
            release_dict.pop("projectslug#version#candidate")
    else:
        release_dict["branches"] = local.read_git_release(release_dict["version"])

    config.write_config(release_dict)


def roll():
    releases_dict = config.read_config()

    sh.git.fetch("--all")

    print("Creating " + helper.get_next_release_candidate() + " ...")

    # Change this so that "master" is configurable
    try:
        try:
            sh.git.checkout("-b", helper.get_next_release_candidate(), "master", _err=sys.stderr, _out=sys.stdout)
        except sh.ErrorReturnCode_1:
            return

        releases_dict["candidate"] = int(releases_dict["candidate"]) + 1
        config.write_config(releases_dict)
        # TODO: Write config to API or Local
        if helper.use_api_share():
            pass
        else:
            local.write_git_release(releases_dict["version"], releases_dict["branches"])
            sh.git.add("releases/release-v{}".format(releases_dict["version"]))
            sh.git.commit("-m", "Appending Release Branch Definition file")
    except sh.ErrorReturnCode_128:
        sys.exit()

    result = subprocess.run(['git', 'config', '--get-all', 'releases.branches'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()

    merge_branches(branches)

    has_conflicts = find_conflicts()
    if has_conflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        print("Pushing to origin")
        print("git push origin " + helper.get_current_release_candidate())
        #sh.git.push("origin", helper.get_current_release_candidate())


def next():
    releases_dict = config.read_config()

    sh.git.fetch("--all")

    print("Creating " + helper.get_next_release_candidate() + " ...")

    # Change this so that "master" is configurable
    try:
        sh.git.checkout("-b", helper.get_next_release_candidate(), helper.get_current_release_candidate(), _err=sys.stderr)
        releases_dict["candidate"] = int(releases_dict["candidate"]) + 1
        config.write_config(releases_dict)
        # TODO: Write config to API or Local
        if helper.use_api_share():
            pass
        else:
            local.write_git_release(releases_dict["version"], releases_dict["branches"])
            sh.git.add("releases/release-v{}".format(releases_dict["version"]))
            sh.git.commit("-m", "Appending Release Branch Definition file")
    except sh.ErrorReturnCode_128 as err:
        print(err)
        sys.exit()

    merge_branches(releases_dict["branches"])

    has_conflicts = find_conflicts()
    if has_conflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        print("git push origin " + helper.get_current_release_candidate())
        #sh.git.push("origin", helper.get_current_release_candidate())


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
        except sh.ErrorReturnCode_128:
            continue
    return


def find_conflicts():
    print()
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