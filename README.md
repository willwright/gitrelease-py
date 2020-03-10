# gitrelease-py
## Installation
### MacOS

### WLS (Windows Linux Subsystem)

## Usage
## Compilation
### MacOS

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