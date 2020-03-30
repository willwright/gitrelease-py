import re
import subprocess
import sys

import click
import copy

import api
import jira
import mygit
from utils import helper


@click.group()
def cli():
    # This definition has to come before all the others other wise @cli will be undefined
    pass


@cli.command()
@click.argument('direction', type=click.Choice([jira.sync.Direction.UP.value, jira.sync.Direction.DOWN.value]))
def jira(direction):
    """
    Updates the branches in this release from JIRA or updates JIRA with the branches in this release.

    remote: update JIRA

    local: update gitrelease
    """
    if direction == jira.sync.Direction.UP.value:
        jira.sync.up()
    elif direction == jira.sync.Direction.DOWN.value:
        jira.sync.down()

    return


@cli.command()
@click.argument('search', type=str, required=False)
def rm(search):
    """
    Removes a branch from the release

    SEARCH: a needle to search for in branch haystack
    """
    release_dict_read = mygit.config.read_config()
    release_dict_write = copy.deepcopy(release_dict_read)

    # No branches found
    if len(release_dict_read["branches"]) <= 0:
        click.secho("No branches found", fg='red')
        return

    print("Branches found:")
    search_match_branch_index = []
    for i in range(0, len(release_dict_read["branches"])):
        if search and search in release_dict_read["branches"][i]:
            click.secho("{}: {} <---".format(i, release_dict_read["branches"][i]), fg='blue')
            search_match_branch_index.append(i)
        else:
            click.secho("{}: {}".format(i, release_dict_read["branches"][i]))

    # If there is only one branch in the list to show, default the prompt to that branch
    if len(search_match_branch_index) == 1:
        default = search_match_branch_index[0]
    else:
        default = "x"

    choice = click.prompt("Select a branch to remove (x = cancel)", type=str, default=default)
    try:
        choice = int(choice)
    except:
        return

    # Remove the FixVersion in JIRA
    jira_send = click.prompt("Update JIRA fixVersion", type=click.Choice(["y", "n"], case_sensitive=False), default="y")

    if jira_send == "y":
        jira_send = True
    else:
        jira_send = False

    if jira_send:
        jira_key = helper.parse_jira_key(release_dict_read["branches"][choice])
        api.jira.delete_fixversion(jira_key, release_dict_read["version"])

    # Remove the branch from the Dictionary
    del release_dict_write["branches"][choice]

    # Write the dictionary to git-config
    mygit.config.write_config(release_dict_write)

    click.secho("Removed: {}".format(release_dict_read["branches"][choice]), fg='green')
    print()

    # @TODO: change to conditional based on configuration
    # Write the dictionary to DynamoDB
    api.awsgateway.writerelease(release_dict_write)

    show_status()

    return


@cli.command()
@click.argument('search', type=str, required=False)
def feature(search):
    """
    Add a feature to the release.

    SEARCH: search branches haystack for the given SEARCH term
    """
    release_dict_read = mygit.config.read_config()
    release_dict_write = copy.deepcopy(release_dict_read)

    branch = find_feature(search)
    if branch:
        if branch in release_dict_read["branches"]:
            print("{}: is already included in this release. Skipping...".format(branch))
            return

        jira_send = click.prompt("Update JIRA fixVersion", type=click.Choice(["y", "n"], case_sensitive=False),
                                 default="y")

        if jira_send == "y":
            jira_key = helper.parse_jira_key(branch)
            api.jira.add_fixveresion(jira_key, release_dict_read["version"])

        # Add the branch to the release dictionary
        release_dict_write["branches"].append(branch)

        # Write the dictionary to git-config
        mygit.config.write_config(release_dict_write)

        # @TODO: Add API configuration conditional
        # Write the dictionary to DynamoDB
        api.awsgateway.writerelease(release_dict_write)

        click.secho("Added: {}".format(branch), fg='green')

    print()
    show_status()

    return


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

    branches = helper.find_branch_by_query(feature_query)

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


@cli.command()
def init():
    """
    Initialize a release.
    """
    release_dict_read = mygit.config.read_config()
    release_dict_write = copy.deepcopy(release_dict_read)

    if "masterbranch" not in release_dict_read or not release_dict_read["masterbranch"]:
        master_branch_choice = click.prompt("Set the master branch", type=str)
        if master_branch_choice:
            release_dict_write["masterbranch"] = master_branch_choice.strip()

    if "stagebranch" not in release_dict_read or not release_dict_read["stagebranch"]:
        stage_branch_choice = click.prompt("Set the stage branch", type=str)
        if stage_branch_choice:
            release_dict_write["stagebranch"] = stage_branch_choice.strip()

    if "devbranch" not in release_dict_read or not release_dict_read["devbranch"]:
        dev_branch_choice = click.prompt("Set the dev branch", type=str)
        if dev_branch_choice:
            release_dict_write["devbranch"] = dev_branch_choice.strip()

    if "projectslug" in release_dict_read and release_dict_read["projectslug"]:
        projectslug = click.prompt("Choose a projectslug", default=release_dict_read["projectslug"], type=str)
    else:
        projectslug = click.prompt("Choose a projectslug", type=str)

    if projectslug:
        release_dict_write["projectslug"] = projectslug.strip()

    # TODO: Check that the slug and version don't already exist; if they do prompt for confirmation
    # if slugExists(projectslug):
    #    print("That slug already exists")
    #    # TODO: Implement a confirmation here

    if "version" in release_dict_read and release_dict_read["version"]:
        default = release_dict_read["version"]
    else:
        default = None

    release_version = click.prompt("Enter Release Version (e.g. 16_07 or 1.0.0)", type=str, default=default)
    release_version = release_version.strip()
    if not release_version:
        click.echo("Release Version is required")
        return

    release_dict_write["version"] = release_version
    release_dict_write["current"] = "release-v" + release_version

    if "candidate" in release_dict_read and release_dict_read["candidate"]:
        default = release_dict_read["candidate"]
    else:
        default = 0

    release_candidate = click.prompt(
        "Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1)", type=int, default=default)
    release_dict_write["candidate"] = int(release_candidate.strip())

    choice = click.prompt("Clear branches (or inherit from current config)", type=click.Choice(["y", "n"]), default="n")

    if choice == "y":
        release_dict_write["branches"].clear()
    elif choice != "n":
        return

    # Write release to config
    mygit.config.write_config(release_dict_write)

    # Write release to API
    api.awsgateway.writerelease(release_dict_write)

    show_status()

    return


@cli.command()
@click.option('-b', '--branches', 'branches', is_flag=True)
def checkout(branches):
    # Read in the config from gitconfig
    release_dict = mygit.config.read_config()

    # git fetch so that our project is up to date
    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)
    click.echo("Getting Release Branches...")

    # Get the list of branches which we identify as "release" branches
    branches_list = helper.find_branch_by_query("origin/release-v")
    if len(branches_list) <= 0:
        click.echo("No Release Branches found in repo")

    # Remove "remotes/" from the beginning of the branch name
    branches_list = map(lambda x: x.replace("remotes/", "", 1), branches_list)

    # Sort the branches by version, candidate
    branches_list = sorted(branches_list, key=helper.release_branch_comp, reverse=False)

    # Print of the list of branches in choice format
    for key in range(0, len(branches_list)):
        largest_tag = False
        if len(branches_list) == 1:
            largest_tag = True
        elif key + 1 >= len(branches_list):
            largest_tag = True
        else:
            regex = re.search("[\d+\.]+\d+", branches_list[key])
            version = regex.group()

            regex = re.search("[\d+\.]+\d+", branches_list[key + 1])
            version_next = regex.group()

            if version_next > version:
                largest_tag = True

        if largest_tag:
            click.secho("{}: {} <---".format(str.rjust(str(key), 3), branches_list[key]), fg="green")
        else:
            click.secho("{}: {}".format(str.rjust(str(key), 3), branches_list[key]))

        # If the branches flag was given
        # print out the branches contained within the given release-vX.XX.X-rcXX
        if branches:
            for branch in api.git.get_branches_in_release(branches_list[key]):
                click.secho("     --{}".format(branch), fg="blue")

    # Prompt the user to select a release-rc
    choice = click.prompt("Choose release (x = cancel)", type=str, default=str(len(branches_list) - 1))
    if choice.strip().lower() == "x":
        return
    else:
        try:
            choice = int(choice)
        except:
            return

    choice_branch = branches_list[choice]

    # Checkout the chosen release-rc
    try:
        subprocess.run(["git", "checkout", choice_branch.replace("origin/", "", 1)], check=True, stdout=sys.stdout,
                       stderr=sys.stderr)
    except subprocess.CalledProcessError:
        click.secho("Checkout Failed; see stderr output above", fg='red')
        return

    # There are two methods for updating the gitconfig
    # Read from the API
    # or
    # Read from the releases/release-vX.XX.X file in the repo
    if helper.use_api_share():
        # Update release_dict from the API
        raw_candidate = api.awsgateway.read_candidate(release_dict)
        if "Item" in raw_candidate:
            release_dict = raw_candidate["Item"]
            release_dict.pop("projectslug#version#candidate")
    else:
        # Update release_dict from the repo
        regex = re.search("[\d+\.]+\d+", choice_branch)
        version = regex.group()

        regex = re.search("\d+$", choice_branch)
        candidate = regex.group()

        release_dict["version"] = version
        release_dict["candidate"] = candidate
        release_dict["branches"] = mygit.releases.read_git_release(release_dict["version"])

    # Write the gitconfig
    mygit.config.write_config(release_dict)

    # Show status of the newly checked out release-rc
    show_status()

    return


@cli.command()
def roll():
    releases_dict = mygit.config.read_config()

    # sh.git.fetch("--all")
    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)

    print("Creating " + helper.get_next_release_candidate() + " ...")

    # Change this so that "master" is configurable
    try:
        try:
            # sh.git.checkout("-b", helper.get_next_release_candidate(), "origin/master", "--no-track", _err=sys.stderr, _out=sys.stdout)
            subprocess.run(
                ["git", "checkout", "-b", helper.get_next_release_candidate(), "origin/master", "--no-track"],
                stderr=sys.stderr, stdout=sys.stdout)
        except:
            return

        releases_dict["candidate"] = int(releases_dict["candidate"]) + 1
        mygit.config.write_config(releases_dict)

        # TODO: Write config to API or Local
        if helper.use_api_share():
            pass
        else:
            mygit.releases.write_git_release(releases_dict["version"], releases_dict["branches"])
            # sh.git.add("releases/release-v{}".format(releases_dict["version"]))
            subprocess.run(["git", "add", "releases/release-v{}".format(releases_dict["version"])], stderr=sys.stderr,
                           stdout=sys.stdout)
            # sh.git.commit("-m", "Appending Release Branch Definition file")
            subprocess.run(["git", "commit", "-m", "Appending Release Branch Definition file"], stderr=sys.stderr,
                           stdout=sys.stdout)
    except:
        sys.exit()

    # @TODO: There is some warning about piping from subprocess.run, read the docs and refactor
    result = subprocess.run(['git', 'config', '--get-all', 'releases.branches'], stdout=subprocess.PIPE)
    branches = result.stdout.decode('utf-8').splitlines()

    merge_branches(branches)

    has_conflicts = find_conflicts()
    if has_conflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        # sh.git.push("-u", "origin", helper.get_current_release_candidate(), _out=sys.stdout)
        subprocess.run(["git", "push", "-u", "origin", helper.get_current_release_candidate()], stderr=sys.stderr,
                       stdout=sys.stdout)

    return


@cli.command()
def next():
    releases_dict = mygit.config.read_config()

    # sh.git.fetch("--all")
    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)

    print("Creating " + helper.get_next_release_candidate() + " ...")

    # @TODO: Change this so that "master" is configurable
    try:
        subprocess.run(["git", "checkout", "--no-track", "-b", helper.get_next_release_candidate(),
                        helper.get_origin_branch_name(helper.get_current_release_candidate())], stderr=sys.stderr,
                       check=True)
    except subprocess.CalledProcessError as err:
        click.secho("Error creating the next release branch. This usually happens when there is a local release "
                    "candidate that has not been pushed to origin", fg='red')
        sys.exit()

    releases_dict["candidate"] = int(releases_dict["candidate"]) + 1
    mygit.config.write_config(releases_dict)

    # TODO: Write config to API or Local
    if helper.use_api_share():
        pass
    else:
        mygit.releases.write_git_release(releases_dict["version"], releases_dict["branches"])
        # sh.git.add("releases/release-v{}".format(releases_dict["version"]))
        subprocess.run(["git", "add", "releases/release-v{}".format(releases_dict["version"])], stderr=sys.stderr,
                       stdout=sys.stdout)
        try:
            # sh.git.commit("-m", "Appending Release Branch Definition file")
            subprocess.run(["git", "commit", "-m", "Appending Release Branch Definition file"], stderr=sys.stderr,
                           stdout=sys.stdout)
        except:
            sys.exit()

    merge_branches(releases_dict["branches"])

    has_conflicts = find_conflicts()
    if has_conflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        # sh.git.push("-u", "origin", helper.get_current_release_candidate())
        subprocess.run(["git", "push", "-u", "origin", helper.get_current_release_candidate()], stdout=sys.stdout,
                       stderr=sys.stderr)

    return


@cli.command()
def status():
    show_status()
    return


def show_status():
    releases_dict = mygit.config.read_config()

    click.echo("Master Branch: {}".format(releases_dict["masterbranch"] if "masterbranch" in releases_dict else "None"))
    click.echo("Staging Branch: {}".format(releases_dict["stagebranch"] if "stagebranch" in releases_dict else "None"))
    click.echo("Development Branch: {}".format(releases_dict["devbranch"] if "devbranch" in releases_dict else "None"))
    click.echo("Checked out Branch: {}".format(helper.get_current_checkout_branch()))
    click.echo("----------------------------------------------")
    click.echo("Current Version: {}".format(releases_dict["version"]))
    click.echo("Current Candidate: {}".format(releases_dict["candidate"]))
    click.echo()
    click.echo("Branches in this release:")
    for branch in releases_dict["branches"]:
        click.echo(branch)

    return


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


def find_conflicts():
    print()
    print("Looking for conflicts with merge.")
    result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], stdout=subprocess.PIPE)
    conflicts = result.stdout.decode('utf-8')

    if conflicts:
        return True
    else:
        return False


@cli.command()
@click.option('-s', '--squash', 'squash', is_flag=True)
@click.argument('environment', type=click.Choice(["dev", "stage", "prod"]))
def deploy(environment, squash):
    releases_dict = mygit.config.read_config()

    if environment == "dev":
        branch_code = "devbranch"
    elif environment == "stage":
        branch_code = "stagebranch"
    elif environment == "prod":
        branch_code = "masterbranch"

    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)

    subprocess.run(["git", "checkout", releases_dict[branch_code]], stdout=sys.stdout, stderr=sys.stderr)

    if environment != "prod":
        subprocess.run(["git", "reset", "--hard",
                        helper.get_origin_branch_name(releases_dict["masterbranch"])],
                       stdout=sys.stdout, stderr=sys.stderr)

    elif environment == "prod":
        subprocess.run(["git", "pull"], stdout=sys.stdout, stderr=sys.stderr)

    if not branch_code:
        return

    try:
        if squash:
            # squash merge
            subprocess.run(["git", "merge", "--squash",
                            "origin/release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"])],
                           stderr=sys.stderr, stdout=sys.stdout)
            subprocess.run(["git", "commit", "-m",
                            "Squash merge: origin/release-v{}-rc{}".format(releases_dict["version"],
                                                                           releases_dict["candidate"])],
                           stderr=sys.stderr, stdout=sys.stdout)
        else:
            # Traditional merge strategy
            subprocess.run(["git", "merge", "--no-ff", "--no-edit",
                            "origin/release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"])],
                           stderr=sys.stderr, stdout=sys.stdout)
    except:
        pass

    subprocess.run(["git", "push", "origin", releases_dict[branch_code], "-f"], stderr=sys.stderr,
                   stdout=sys.stdout)
    # TODO: If prod then tag

    return


@cli.command()
@click.argument('keepbranches', type=int)
def prune(keepbranches):
    # Read in the config from gitconfig
    release_dict = mygit.config.read_config()

    # git fetch so that our project is up to date
    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)
    click.echo("Getting Release Branches...")

    # Get the list of branches which we identify as "release" branches
    branches_list = helper.find_branch_by_query("origin/release-v{}".format(release_dict['version']))
    if len(branches_list) <= 0:
        click.echo("No Release Branches found in repo")

    # Remove "remotes/" from the beginning of the branch name
    branches_list = map(lambda x: x.replace("remotes/", "", 1), branches_list)

    # Remove "origin/" from the beginning of the branch name
    branches_list = map(lambda x: x.replace("origin/", "", 1), branches_list)

    # Sort the branches by version, candidate
    branches_list = sorted(branches_list, key=helper.release_branch_comp, reverse=False)
    # print(branches_list)

    if len(branches_list) <= keepbranches:
        click.echo("Length less than {}. Nothing to do".format(keepbranches))
        return

    print()
    for x in range(0, len(branches_list) - keepbranches):
        # Delete local branch
        print("{}".format(branches_list[x]))

    if not click.confirm("The above branches are going to be permanently deleted; continue?"):
        return

    for x in range(0, len(branches_list) - keepbranches):
        # Delete local branch
        try:
            process = subprocess.run(["git", "branch", "-D", branches_list[x]], stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, check=True, encoding='utf-8')
            if process.stdout:
                click.secho(process.stdout, fg='green')
            if process.stderr:
                click.secho(process.stderr, fg='green')
        except subprocess.CalledProcessError as err:
            click.secho(err.stderr, fg='red')

        # Delete remote branch
        for origin in mygit.config.get_remote_list():
            try:
                process = subprocess.run(["git", "push", origin, "--delete", branches_list[x]], check=True,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
                if process.stdout:
                    click.secho(process.stdout, fg='green')
                if process.stderr:
                    click.secho(process.stderr, fg='green')
            except subprocess.CalledProcessError as err:
                click.secho(err.stderr, fg='red')

    print()
    # Get new list of origin branches
    branches_list = helper.find_branch_by_query("origin/release-v{}".format(release_dict['version']))

    # Sort the branches by version, candidate
    branches_list = sorted(branches_list, key=helper.release_branch_comp, reverse=False)
    for branch in branches_list:
        print(branch)

    return


@cli.command()
def append():
    releases_dict_read = mygit.config.read_config()
    releases_dict_write = copy.deepcopy(releases_dict_read)

    subprocess.run(["git", "fetch", "--all"], stdout=sys.stdout, stderr=sys.stderr)

    try:
        subprocess.run(["git", "pull"], stderr=sys.stderr)

        # TODO: Write config to API or Local
        if helper.use_api_share():
            pass
        else:
            mygit.releases.write_git_release(releases_dict_read["version"], releases_dict_read["branches"])
            subprocess.run(["git", "add", "releases/release-v{}".format(releases_dict_read["version"])],
                           stderr=sys.stderr,
                           stdout=sys.stdout)
            try:
                subprocess.run(["git", "commit", "-m", "Appending Release Branch Definition file"], stderr=sys.stderr,
                               stdout=sys.stdout)
            except:
                pass
    except:
        sys.exit()

    merge_branches(releases_dict_read["branches"])

    has_conflicts = find_conflicts()
    if has_conflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        subprocess.run(["git", "push", "-u", "origin", helper.get_current_release_candidate()], stdout=sys.stdout,
                       stderr=sys.stderr)

    return


if __name__ == '__main__':
    cli()
