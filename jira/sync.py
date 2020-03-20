import api
from enum import Enum
from utils import helper
import mygit


class Direction(Enum):
    UP = "up"
    DOWN = "down"


def up():
    releases_dict = mygit.config.read_config()

    # Get all issues in project/version
    issues_list = api.jira.search_issues(releases_dict["projectslug"], releases_dict["version"])

    # Add any missing branches
    for branch in releases_dict["branches"]:
        found = False
        for issue in issues_list:
            if helper.parse_jira_key(branch) in issue:
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
                api.jira.create_fixveresion(helper.parse_jira_key(branch), releases_dict["version"])
            elif int(choice) == 1:
                releases_dict["branches"].remove(branch)
                continue
            elif int(choice) == 2:
                continue
            else:
                continue
    mygit.config.write_config(releases_dict)
    return


def down():
    releases_dict = mygit.config.read_config()

    # Get all issues in project/version
    issues_list = api.jira.search_issues(releases_dict["projectslug"], releases_dict["version"])

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
                if len(branches) <= 0:
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
                api.jira.delete_fixversion(issue, releases_dict["version"])
                print("Removed {} from {}".format(issue, releases_dict["version"]))
                print()
            elif int(choice) == 2:
                continue
            else:
                continue

    mygit.config.write_config(releases_dict)
    return
