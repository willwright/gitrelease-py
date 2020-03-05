import api
import click
import helper
import jira
import mygit
import re
import sh
import subprocess
import sys


@click.command()
@click.argument('direction', type=click.Choice([jira.sync.Direction.UP.value, jira.sync.Direction.DOWN.value]))
def jirasync(direction):

    if direction == jira.sync.Direction.UP.value:
        jira.sync.up()
    elif direction == jira.sync.Direction.DOWN.value:
        jira.sync.down()

    return


@click.command()
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


@click.command()
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
            api.jira.create_fixveresion(jira_key, release_dict["version"])

    show_status()

    return


def find_feature():
    print("Find a branch by type, or search for it by name")
    print("0: Search by name")
    print("1: List all feature/ branches")
    print("2: List all bugfix/ branches")
    print("3: List all hotfix/ branches")

    search_type = click.prompt("Search by", type=int, default=0)

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


@click.command()
def init():
    release_dict = mygit.config.read_config()
    if "projectslug" in release_dict and release_dict["projectslug"]:
        projectslug = click.prompt("Choose a projectslug", default=release_dict["projectslug"], type=str)
    else:
        projectslug = click.prompt("Choose a projectslug ", type=str)

    release_dict["projectslug"] = projectslug.strip()

    # TODO: Check that the slug and version don't already exist; if they do prompt for confirmation
    #if slugExists(projectslug):
    #    print("That slug already exists")
    #    # TODO: Implement a confirmation here

    release_version = click.prompt("Enter Release Version (e.g. 16_07 or 1.0.0)", type=str)
    release_version = release_version.strip()
    if not release_version:
        click.echo("Release Version is required")
        return

    release_dict["version"] = release_version
    release_dict["current"] = "release-v" + release_version

    release_candidate = click.prompt("Enter Release Candidate Version (e.g. 1,2,3... or blank for 0, first roll will be 1)", type=int, default=0)
    release_dict["candidate"] = int(release_candidate)

    show_status()

    choice = click.prompt("Clear branches (or inherit from current config)", type=click.Choice(["y", "n"]), default="n")

    if choice == "y":
        mygit.config.clearbranches()
    elif choice != "n":
        return

    # Write release to config
    mygit.config.write_config(release_dict)

    # Write release to API
    api.awsgateway.writerelease(release_dict)

    return


@click.command()
def checkout():
    # Read in the config from gitconfig
    release_dict = mygit.config.read_config()

    # git fetch so that our project is up to date
    sh.git.fetch("--all")
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
        elif key+1 >= len(branches_list):
            largest_tag = True
        else:
            regex = re.search("[\d+\.]+\d+", branches_list[key])
            version = regex.group()

            regex = re.search("[\d+\.]+\d+", branches_list[key+1])
            version_next = regex.group()

            if version_next > version:
                largest_tag = True

        if largest_tag:
            click.secho("{}: {} <---".format(str.rjust(str(key), 3), branches_list[key]), fg="green")
        else:
            click.echo("{}: {}".format(str.rjust(str(key), 3), branches_list[key]))

    choice = click.prompt("Choose release (x = cancel)", type=str, default="x")
    if choice.strip().lower() == "x":
        return
    else:
        try:
            choice = int(choice)
        except:
            return

    choice_branch = branches_list[choice]
    sh.git.checkout(choice_branch.replace("origin/", "", 1))

    if helper.use_api_share():
        # Update release_dict from the API
        raw_candidate = api.awsgateway.read_candidate(release_dict)
        if "Item" in raw_candidate:
            release_dict = raw_candidate["Item"]
            release_dict.pop("projectslug#version#candidate")
    else:
        regex = re.search("[\d+\.]+\d+", choice_branch)
        version = regex.group()

        regex = re.search("\d+$", choice_branch)
        candidate = regex.group()

        release_dict["version"] = version
        release_dict["candidate"] = candidate
        release_dict["branches"] = mygit.releases.read_git_release(release_dict["version"])

    mygit.config.write_config(release_dict)

    show_status()

    return


def roll():
    releases_dict = mygit.config.read_config()

    sh.git.fetch("--all")

    print("Creating " + helper.get_next_release_candidate() + " ...")

    # Change this so that "master" is configurable
    try:
        try:
            sh.git.checkout("-b", helper.get_next_release_candidate(), "origin/master", "--no-track", _err=sys.stderr, _out=sys.stdout)
        except sh.ErrorReturnCode_1:
            return

        releases_dict["candidate"] = int(releases_dict["candidate"]) + 1
        mygit.config.write_config(releases_dict)

        # TODO: Write config to API or Local
        if helper.use_api_share():
            pass
        else:
            mygit.releases.write_git_release(releases_dict["version"], releases_dict["branches"])
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
        sh.git.push("-u", "origin", helper.get_current_release_candidate(), _out=sys.stdout)

    return


def next():
    releases_dict = mygit.config.read_config()

    sh.git.fetch("--all")

    print("Creating " + helper.get_next_release_candidate() + " ...")

    # Change this so that "master" is configurable
    try:
        # TODO: Checkout from origin with --no-track; add -u on the push
        sh.git.checkout("-b", helper.get_next_release_candidate(), helper.get_origin_branch_name(helper.get_current_release_candidate()), _err=sys.stderr)
        releases_dict["candidate"] = int(releases_dict["candidate"]) + 1
        mygit.config.write_config(releases_dict)

        # TODO: Write config to API or Local
        if helper.use_api_share():
            pass
        else:
            mygit.releases.write_git_release(releases_dict["version"], releases_dict["branches"])
            sh.git.add("releases/release-v{}".format(releases_dict["version"]))
            try:
                sh.git.commit("-m", "Appending Release Branch Definition file")
            except sh.ErrorReturnCode_1:
                pass
    except sh.ErrorReturnCode_128 as err:
        print(err)
        sys.exit()

    merge_branches(releases_dict["branches"])

    has_conflicts = find_conflicts()
    if has_conflicts:
        print("Not pushing to origin")
    else:
        print("Pushing to origin")
        sh.git.push("-u", "origin", helper.get_current_release_candidate())

    return


@click.command()
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
    sh.git.fetch("--all")

    for branch in branches:
        branch = branch.strip()
        print()
        print("Merging: " + branch)
        try:
            sh.git.merge("--no-ff", "--no-edit", branch, _err=sys.stderr, _out=sys.stdout)
        except sh.ErrorReturnCode_1:
            continue
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


def deploy():
    releases_dict = mygit.config.read_config()

    if len(sys.argv) < 2:
        print("no env specified")

    env = sys.argv[2]

    if env == "dev":
        branch_code = "devbranch"
    elif env == "stage":
        branch_code = "stagebranch"
    elif env == "prod":
        branch_code = "masterbranch"

    sh.git.fetch("--all", _out=sys.stdout)
    sh.git.checkout(releases_dict[branch_code], _out=sys.stdout)
    if env != "prod":
        sh.git.reset("--hard", helper.get_origin_branch_name(releases_dict["masterbranch"]), _out=sys.stdout)
    elif env == "prod":
        sh.git.pull()

    if not branch_code:
        return

    try:
        # Traditional merge strategy
        # sh.git.merge("--no-ff", "--no-edit", "origin/release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"]), _err=sys.stderr, _out=sys.stdout)

        # squash merge
        sh.git.merge("--squash", "origin/release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"]), _err=sys.stderr)
        sh.git.commit("-m", "Squash merge: origin/release-v{}-rc{}".format(releases_dict["version"], releases_dict["candidate"]))
    except:
        pass

    sh.git.push("origin", releases_dict[branch_code], "-f", _err=sys.stderr, _out=sys.stdout)
    # TODO: If prod then tag

    return


@click.group()
def cli():
    pass


cli.add_command(status)
cli.add_command(checkout)
cli.add_command(rm)
cli.add_command(feature)
cli.add_command(jirasync)
cli.add_command(init)
