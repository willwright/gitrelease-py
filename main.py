#!/usr/bin/python

import git
import api
import config
from git import Repo
import os
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
    config.write_release(release_dict)

    # Write release to API
    api.writerelease(release_dict)


def checkout():
    

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


def main(argv):
    method = argv[1]+"()"
    exec(method)


if __name__ == "__main__":
    main(sys.argv)