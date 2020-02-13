#!/usr/bin/python

import git
from git import Repo
import os
import sys
import sh

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
    releaseVersion = raw_input("Enter Release Version (e.g. 16_07 or 1.0.0):")
    releaseVersion = releaseVersion.strip()
    assert releaseVersion, "Release Version is required"
    sh.git.config("--local", "--replace-all", "releases.version", releaseVersion)

    releaseCandidate = 0
    input("Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1):")
    sh.git.config("--local", "--replace-all", "releases.candidate", releaseCandidate)

    sh.git.config("--local", "--replace-all", "releases.current", "release-v" + releaseVersion)

    clearbranches()


def roll():
    nextReleaseBranch = getNextReleaseBranch()

    sh.git.fetch("--all")

    print("Creating " + nextReleaseBranch + "...")

    # Change this so that "master" is configurable
    sh.git.checkout("-b", nextReleaseBranch, "master")

    branches = sh.git.config("--local", "--get-all", "releases.branches")
    mergeBranches(branches)


def mergeBranches(branches):
    sh.git.fetch("--all")

    for branch in branches:
        print("Merging: " + branch + " ++++++++++++++++++++++++")
        sh.git.merge("--no-edit", "--squash", branch)


def getCurrent():
    return str(sh.git.config("--local", "--get", "releases.current").strip())


def getCandidate():
    return int(sh.git.config("--local", "--get", "releases.candidate").strip())


def getNextReleaseBranch():
    current = getCurrent()
    candidate = getCandidate()
    return "{current}-rc{candidate}".format(current=current, candidate=candidate+1)


def main(argv):
    method = argv[1]+"()"
    exec(method)

if __name__ == "__main__":
    main(sys.argv)