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
def jirasync(direction):
    if direction == jira.sync.Direction.UP.value:
        jira.sync.up()
    elif direction == jira.sync.Direction.DOWN.value:
        jira.sync.down()

    return


@cli.command()
def rm():
    print("Branches found:")
    release_dict = mygit.config.read_config()
    for i in range(0, len(release_dict["branches"])):
        print("{}: {}".format(i, release_dict["branches"][i]))

    choice = click.prompt("Select a branch to remove (x = cancel)", type=str, default="x")
    if choice.lower().strip() == "x":
        return
    else:
        try:
            choice = int(choice)
        except:
            return

    # Remove the FixVersion in JIRA
    jira_send = click.prompt("Send to JIRA:", type=click.Choice(["y", "n"], case_sensitive=False), default="y")

    if jira_send == "y":
        jira_send = True
    else:
        jira_send = False

    if jira_send:
        jira_key = helper.parse_jira_key(release_dict["branches"][choice])
        api.jira.delete_fixversion(jira_key, release_dict["version"])

    # Remove the branch from the Dictionary
    del release_dict["branches"][choice]

    # Write the dictionary to git-config
    mygit.config.write_config(release_dict)

    # Write the dictionary to DynamoDB
    api.awsgateway.writerelease(release_dict)

    show_status()

    return


@cli.command()
def feature():
    release_dict = mygit.config.read_config()

    branch = find_feature()
    if branch:
        if branch in release_dict["branches"]:
            print("{}: is already included in this release. Skipping...".format(branch))
            return

        # Add the branch to the release dictionary
        release_dict["branches"].append(branch)
        # Write the dictionary to git-config
        mygit.config.write_config(release_dict)
        # Write the dictionary to DynamoDB
        api.awsgateway.writerelease(release_dict)

        jira_send = click.prompt("Send to JIRA", type=click.Choice(["y", "n"], case_sensitive=False), default="y")

        if jira_send == "y":
            jira_send = True
        else:
            jira_send = False

        if jira_send:
            jira_key = helper.parse_jira_key(branch)
            api.jira.add_fixveresion(jira_key, release_dict["version"])

    show_status()

    return


def find_feature():
    print("Find a branch by type, or search for it by name")
    print("0: Search by name")
    print("1: List all feature/ branches")
    print("2: List all bugfix/ branches")
    print("3: List all hotfix/ branches")

    search_type = click.prompt("Search by", type=click.IntRange(0, 3), default=0)

    feature_query = ""
    if search_type == 0:
        feature_query = click.prompt("Enter part of a Feature Branch name (we will search for it)", type=str).strip()
    elif search_type == 1:
        feature_query = "feature/"
    elif search_type == 2:
        feature_query = "bugfix/"
    elif search_type == 3:
        feature_query = "hotfix/"
    else:
        return

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


@cli.command()
def init():
    release_dict = mygit.config.read_config()
    if "projectslug" in release_dict and release_dict["projectslug"]:
        projectslug = click.prompt("Choose a projectslug", default=release_dict["projectslug"], type=str)
    else:
        projectslug = click.prompt("Choose a projectslug", type=str)

    release_dict["projectslug"] = projectslug.strip()

    # TODO: Check that the slug and version don't already exist; if they do prompt for confirmation
    # if slugExists(projectslug):
    #    print("That slug already exists")
    #    # TODO: Implement a confirmation here

    release_version = click.prompt("Enter Release Version (e.g. 16_07 or 1.0.0)", type=str)
    release_version = release_version.strip()
    if not release_version:
        click.echo("Release Version is required")
        return

    release_dict["version"] = release_version
    release_dict["current"] = "release-v" + release_version

    release_candidate = click.prompt(
        "Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1)", type=int, default=0)
    release_dict["candidate"] = int(release_candidate)

    show_status()

    choice = click.prompt("Clear branches (or inherit from current config)", type=click.Choice(["y", "n"]), default="n")

    if choice == "y":
        release_dict["branches"].clear()
    elif choice != "n":
        return

    # Write release to config
    mygit.config.write_config(release_dict)

    # Write release to API
    api.awsgateway.writerelease(release_dict)

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

    # Change this so that "master" is configurable
    try:
        # TODO: Checkout from origin with --no-track; add -u on the push
        subprocess.run(["git", "checkout", "-b", helper.get_next_release_candidate(),
                        helper.get_origin_branch_name(helper.get_current_release_candidate())], stderr=sys.stderr)
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
                pass
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

    click.echo("Master Branch: {}".format(releases_dict["masterbranch"]))
    click.echo("Staging Branch: {}".format(releases_dict["stagebranch"]))
    click.echo("Development Branch: {}".format(releases_dict["devbranch"]))
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
