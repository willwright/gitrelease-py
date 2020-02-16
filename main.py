#!/usr/bin/python

import git
from git import Repo
import json
import os
import requests
import sh
import subprocess
import sys
import utility

repo = Repo(os.getcwd())
assert not repo.bare, "This directory is a bare repo, please clone a project to work with"


def add(branch):
    sh.git.config("--add", "releases.branches", branch)


def clearbranches():
    # git config --unset-all releases.branches
    sh.git.config("--local", "--unset-all", "releases.branches")


def feature():
    branch = findFeature()
    add(branch)


def findFeature():
    print("Find a branch by type, or search for it by name: ")
    print("0 Search by name")
    print("1 List all feature/ branches")
    print("2 List all bugfix/ branches")
    print("3 List all hotfix/ branches")
    searchType = input()

    if searchType == 0:
        featureQuery = input("Enter part of a Feature Branch name: (we will search for it) ")
    elif searchType == 1:
        featureQuery = "feature/"
    elif searchType == 2:
        featureQuery = "bugfix/"
    elif searchType == 3:
        featureQuery = "hotfix/"

    ffBranches = filter(lambda x: featureQuery in x.name, repo.branches)

    assert len(ffBranches) > 0, "No branches found matching your query"

    option = 0
    for branch in ffBranches:
        print("{option}: {branch}".format(option=option, branch=branch.name))

    chosenBranch = input("Select Branch (x = cancel): ")
    if chosenBranch == "x" or chosenBranch == "X" or chosenBranch == "":
        return

    print("Selected: {branch}".format(branch=ffBranches[chosenBranch]))
    return ffBranches[chosenBranch]


def init():
    projectslug = input("Enter the project slug: ")
    projectslug = projectslug.strip()

    #if slugExists(projectslug):
    #    print("That slug already exists")
    #    # TODO: Implement a confirmation here


    sh.git.config("--local", "--replace-all", "releases.projectslug", projectslug)

    releaseVersion = input("Enter Release Version (e.g. 16_07 or 1.0.0): ")
    releaseVersion = releaseVersion.strip()
    assert releaseVersion, "Release Version is required"
    sh.git.config("--local", "--replace-all", "releases.version", releaseVersion)

    releaseCandidate = 0
    input("Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1): ")
    sh.git.config("--local", "--replace-all", "releases.candidate", releaseCandidate)

    sh.git.config("--local", "--replace-all", "releases.current", "release-v" + releaseVersion)

    #clearbranches()

    # Write release to API
    writerelease()


def roll():

    nextReleaseCandidate = getNextReleaseCandidate()

    sh.git.fetch("--all")

    print("Creating " + nextReleaseCandidate + " ...")

    # Change this so that "master" is configurable
    try:
        sh.git.checkout("-b", nextReleaseCandidate, "master", _err=sys.stderr)
        incrementCandidate()
        writerelease()
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
        writerelease()
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


def readrelease():
    projectslug = getprojectslug()
    version = getversion()
    response = requests.get("https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{0}/release/{1}".format(projectslug, version))

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if response.json():
        utility.write_release(response.json())
    else:
        return False

def writerelease():
    releases_dict = utility.read_config()

    #print()
    #print(json.dumps(releases_dict, indent=4, sort_keys=True))

    response = requests.post('https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/release',
                             data=json.dumps(releases_dict),
                             headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")


def slugExists(projectslug):
    response = requests.get('https://5idtbmykhf.execute-api.us-west-1.amazonaws.com/develop/project/{:s}'.format(projectslug))
    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")

    if "projectslug" in response.json()["item"]:
        return True
    else:
        return False


def main(argv):
    method = argv[1]+"()"
    exec(method)


if __name__ == "__main__":
    main(sys.argv)