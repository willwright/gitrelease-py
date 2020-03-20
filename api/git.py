import helper
import mygit
import re
import requests


def get_branches_in_release(refName):
    # Format refName for use in gitHub GraphQL Query
    # Requires format "release-vX.XX.X-rcYY
    if refName.lower().startswith("origin/"):
        refName = refName.replace("origin/","")

    # Read the remote "origin" > url value from gitconfig
    remoteOriginUrl = mygit.config.read_config_remote_origin()

    # Parse for owner
    owner = get_owner(remoteOriginUrl)
    if owner is None:
        return

    # Parse for repository
    repository = get_repository(remoteOriginUrl)
    if repository is None:
        return

    # Get just "release-vX.XX.X" part
    rcIndex = refName.lower().find('-rc')
    releasePart = refName[0:rcIndex]

    # github GraphQL query
    query = "query {{repository(owner: \"{}\", name:\"{}\") {{ object(expression: \"{}:releases/{}\") {{ ... on Blob {{ text }} }} }} }}".format(owner, repository, refName, releasePart)
    jsonData = {"query": query}

    config_dict = helper.load_configuration()
    response = requests.post('https://api.github.com/graphql',
                             json=jsonData,
                             headers={'Content-Type': 'application/json', 'Authorization': config_dict['github']['bearer']}
                             )

    branchList = []

    if response.status_code != 200:
        # Replace this with raise error
        print("ApiCall Error")
        print(response)
        return branchList
    else:
        try:
            # Parse text response into a List
            text = response.json()['data']['repository']['object']['text']
            branchList = text.split('\n')
            branchList = list(filter(lambda x: not not x, branchList))
            return branchList
        finally:
            return branchList


def get_owner(githubUrl):
    x = re.search("^https:\/\/github\.com\/([\w]*)/([\w]*)", githubUrl)

    if x and x.group(1):
        return x.group(1)


def get_repository(githubUrl):
    x = re.search("^https:\/\/github\.com\/([\w]*)/([\w]*)", githubUrl)

    if x and x.group(2):
        return x.group(2)