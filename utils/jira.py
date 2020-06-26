import copy
from enum import Enum

import click

import api
import mygit
from utils import helper


class Direction(Enum):
    UP = "push"
    DOWN = "pull"


def up():
    releases_dict_read = mygit.config.read_config()
    release_dict_write = copy.deepcopy(releases_dict_read)

    # Get all issues in project/version
    try:
        issues_list = api.jiraapi.search_issues(releases_dict_read["projectslug"], releases_dict_read["version"])
    except Exception as err:
        if 'missing-version' in err.args:
            try:
                api.jiraapi.create_fixversion(releases_dict_read["projectslug"], releases_dict_read["version"])
            except Exception:
                return
            finally:
                click.secho("fixVersion: {} created for project: {}".format(releases_dict_read["version"],
                                                                            releases_dict_read["projectslug"]),
                            fg='green')
                issues_list = api.jiraapi.search_issues(releases_dict_read["projectslug"],
                                                        releases_dict_read["version"])

        else:
            click.secho(err, fg='red')
            return

    # Add any missing branches
    for branch in releases_dict_read["branches"]:
        print()
        found = False
        for issue in issues_list:
            if helper.parse_jira_key(branch).lower() in issue.lower():
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
                    api.jiraapi.add_fixveresion(helper.parse_jira_key(branch), releases_dict_read["version"])
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
    try:
        issues_list = api.jiraapi.search_issues(releases_dict_read["projectslug"], releases_dict_read["version"])
    except Exception as err:
        if 'missing-version' in err.args:
            click.secho(err, fg='red')
        return

    # Add any missing branches
    for issue in issues_list:
        print()
        found = False
        for branch in releases_dict_read["branches"]:
            if issue.lower() in branch.lower():
                click.secho("{}{}".format((branch + " ").ljust(60, '='), "> FOUND"), fg='blue')
                found = True

        if not found:
            click.secho("{}{}".format((issue + " ").ljust(60, '='), "> MISSING"), fg='yellow')
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

                if len(branches) == 1:
                    chosen_branch = click.prompt("Select Branch", type=int, default=0)
                else:
                    chosen_branch = click.prompt("Select Branch", type=click.IntRange(0, len(branches)))

                print("Selected: {branch}".format(branch=branches[chosen_branch]))
                release_dict_write["branches"].append(branches[chosen_branch])
                click.secho("{}{}".format((branches[chosen_branch] + " ").ljust(60, '='), "> ADDED"), fg='green')

            elif choice == 1:
                # Remove from JIRA
                try:
                    api.jiraapi.delete_fixversion(issue, releases_dict_read["version"])
                    click.secho("{}{}".format((issue + " ").ljust(60, '='), "> REMOVED"), fg='green')
                except Exception:
                    pass
                print()

            elif choice == 2:
                # Skip
                click.secho("{}{}".format((issue + " ").ljust(60, '='), "> SKIPPED"), fg='green')

            else:
                pass

    mygit.config.write_config(release_dict_write)
    return
