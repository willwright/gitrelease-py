import json
import subprocess


def getRelease():
    result = subprocess.run(['git', 'config', '--local', '--get-regex', 'releases'], stdout=subprocess.PIPE)
    releasesList = result.stdout.decode('utf-8')
    releasesList = releasesList.splitlines()
    #print(type(releasesList))
    #print(releasesList)

    releasesList = list(map(lambda x: x.split(" "), releasesList))
    #print()
    #print(type(releasesList))
    #print(releasesList)

    releasesDict = {"branches": []}
    for item in releasesList:
        if item[0] == "releases.branches":
            # TODO: Add de-dupe function
            releasesDict["branches"].append(item[1])
        else:
            releasesDict[item[0].replace("releases.", "")] = item[1]

    return releasesDict
