import copy
from enum import Enum

import click

import api
import mygit
from utils import helper


class Direction(Enum):
    UP = "up"
    DOWN = "down"


def up():
    releases_dict_read = mygit.config.read_config()
    release_dict_write = copy.deepcopy(releases_dict_read)

    # Get all issues in project/version
    try:
        issues_list = api.jira.search_issues(releases_dict_read["projectslug"], releases_dict_read["version"])
    except Exception as err:
        if 'missing-version' in err.args:
            try:
                api.jira.create_fixversion(releases_dict_read["projectslug"], releases_dict_read["version"])
            except Exception:
                return
            finally:
                click.secho("fixVersion: {} created for project: {}".format(releases_dict_read["version"], releases_dict_read["projectslug"]), fg='green')
                issues_list = api.jira.search_issues(releases_dict_read["projectslug"], releases_dict_read["version"])

        else:
            click.secho(err, fg='red')
            return

    # Add any missing branches
    for branch in releases_dict_read["branches"]:
        print()
        found = False
        for issue in issues_list:
            if helper.parse_jira_key(branch) in issue:
                click.secho("{}{}".format((branch + " ").ljust(60, '='), "> FOUND"), fg='blue')
                found = True
        if not found:
            click.secho("{}{}".format((branch + " ").ljust(60, '='), "> MISSING"), fg='yellow')
            print("0: Add to JIRA release")
            print("1: Remove from local release")
            print("2: Skip")
            choice = click.prompt("Selection", type=click.IntRange(0, 2), default=0)
            if choice == 0:
                try:
                    api.jira.add_fixveresion(helper.parse_jira_key(branch), releases_dict_read["version"])
                    click.secho("{}{}".format((branch + " ").ljust(60, '='), "> ADDED"), fg='green')
                except Exception:
                    pass
            elif choice == 1:
                release_dict_write["branches"].remove(branch)
                click.secho("{}{}".format((branch + " ").ljust(60, '='), "> REMOVED"), fg='green')
            elif choice == 2:
                # Skip
                click.secho("{}{}".format((branch + " ").ljust(60, '='), "> SKIPPED"), fg='green')
            else:
                pass

    mygit.config.write_config(release_dict_write)
    return


def down():
    releases_dict_read = mygit.config.read_config()
    release_dict_write = copy.deepcopy(releases_dict_read)

    # Get all issues in project/version
    issues_list = api.jira.search_issues(releases_dict_read["projectslug"], releases_dict_read["version"])

    try:
        issues_list = api.jira.search_issues(releases_dict_read["projectslug"], releases_dict_read["version"])
    except Exception as err:
        if 'missing-version' in err.args:
            click.secho(err, fg='red')

        return

    # Add any missing branches
    for issue in issues_list:
        print()
        found = False
        for branch in releases_dict_read["branches"]:
            if issue in branch:
                click.secho("{}{}".format((branch + " ").ljust(60, '='), "> FOUND"), fg='blue')
                found = True

        if not found:
            click.secho("{}{}".format((branch + " ").ljust(60, '='), "> MISSING"), fg='yellow')
            print("0: Add to local release")
            print("1: Remove from JIRA release")
            print("2: Skip")
            choice = click.prompt("Selection", type=click.IntRange(0, 2), default=0)

            if choice == 0:
                # Add to local
                branches = helper.find_branch_by_query(issue)
                if len(branches) <= 0:
                    print("No branches found matching your query")
                    print()
                    continue

                for i in range(0, len(branches)):
                    print("{option}: {branch}".format(option=i, branch=branches[i]))

                chosen_branch = click.prompt("Select Branch (x = cancel): ") or "x"
                if chosen_branch.lower() == "x" or chosen_branch == "":
                    print()
                    continue

                chosen_branch = int(chosen_branch)

                print("Selected: {branch}".format(branch=branches[chosen_branch]))
                print()
                release_dict_write["branches"].append(branches[chosen_branch])

            elif choice == 1:
                # Remove from JIRA
                try:
                    api.jira.delete_fixversion(issue, releases_dict_read["version"])
                    click.secho("{}{}".format((branch + " ").ljust(60, '='), "> REMOVED"), fg='green')
                except Exception:
                    pass
                print()

            elif choice == 2:
                # Skip
                click.secho("{}{}".format((branch + " ").ljust(60, '='), "> SKIPPED"), fg='green')

            else:
                pass

    mygit.config.write_config(release_dict_write)
    return
