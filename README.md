# gitrelease-py
## Installation
### MacOS

### WLS (Windows Linux Subsystem)

## Usage
Running `gitrelease-py` from the command line will display the list of available commands.

The `--help` option can always be applied to a command in order to inspect the command's options and arguments.

### Commands
#### checkout
Checkout a release branch from origin.

#### deploy
Deploy the current release branch to a testing environment. 

Example:

``gitrelease-py deploy dev``

OPTIONS:

**-s, --squash** : Uses squash when merging release to environment branch.

ARGUMENTS:

**dev** : Merges to the configured `devbranch`

**stage** : Merges to the configured `stagebranch`

**prod** : Merges to the configured `masterbranch`

#### feature
Add a feature branch to the current release.

Only remote branches are considered for adding to a release. Local branches are filtered out of the chooser because adding them can cause issues for other team members. 

#### init
Initialize a new release.

#### jirasync
Synchronize the branches in the current release with JIRA. 
 
#### next
Create a new release candidate from the current list of branches. Base for merge is the **highest** release candidate.  

#### rm
Remove a branch from the current list of branches. 
 
#### roll
Create a new release candidate from the current list of branhces. Base for merge is `origin/master`. 

#### status
Show the current release's configured values. 

## Compilation
### MacOS
#### Prerequisites
1. git

Install python 3

`sudo apt-get intall python3`

Create a project directory

`mkdir gitrelease-py-source`

Checkout the source code

`cd gitrelease-py-source`

`git clone https://github.com/willwright/gitrelease-py.git`

Create a Virtual Environment

`pip install virtualenv --user`

`python3 -m venv <myenvname>` (I use "venv" for myenvname)

Activate the virtual environment

`. venv/bin/activate`

Install package requirements

`pip install PyYAML`

`pip install click`

`pip install requests`

Install gitrelease-py

`pip install --editable .`

### WLS (Windows Linux Subsystem)
#### Prerequisites
1. git

Install python 3

`sudo apt-get intall python3`

Create a project directory

`mkdir gitrelease-py-source`

Checkout the source code

`cd gitrelease-py-source`

`git clone https://github.com/willwright/gitrelease-py.git`

Create a Virtual Environment

`pip install virtualenv --user`

`python3 -m venv <myenvname>` (I use "venv" for myenvname)

Activate the virtual environment

`. venv/bin/activate`

Install package requirements

`pip install PyYAML`

`pip install click`

`pip install requests`

Install gitrelease-py

`pip install --editable .`