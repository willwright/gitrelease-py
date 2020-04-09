---
title: Build
description: How to build gitrelease-py from source
---

# Build
This page describes how to make a distributable from source project.

## Prerequisites
* git

## Mac
Checkout the source code from github [willwright/gitrelease-py](https://github.com/willwright/gitrelease-py)

Install python3.8. Example uses [homebrew](https://brew.sh/)
```
brew install python@3.8
```

Add the 3.8 install to your path so that python3 defaults to 3.8 (assumes bash shell)
```
echo 'export PATH="/usr/local/opt/python@3.8/bin:$PATH"' >> ~/.bash_profile
```

Test that your default `python3` version is 3.8
```
# python3 -V
Python 3.8.1
```

Change directory to checked out repo

Create a virtual environment using python3.8
```
python3 -m venv venv
```

Activate the virtual environment
```
. venv/bin/activate
```

Test that the version of your virtual environment is correct
```
# python -V
Python 3.8.1
```

Install dependencies
```
pip install pyinstaller click PyYAML requests
```

Build the distributable
```
pyinstaller --onefile -n gitrelease --hiddenimport click,requests,PyYAML main.py
```

You should see a bunch of output in your console and a single file (`gitrelease`) in the `dist` folder

## Windows
Checkout the source code from github [willwright/gitrelease-py](https://github.com/willwright/gitrelease-py)

Install python3.8. [python/downloads](https://www.python.org/downloads/)

*Note: I had to use the installer from python.org NOT the installer from microsoft store*

When the installers runs choose add to PATH 

Test that your default `python` is version is 3.8
```
PS C:\Users\Will> python -V
Python 3.8.2
PS C:\Users\Will>
```

Change directory to checked out repo

Create a virtual environment using python3.8
```
python -m venv venv
```

Activate the virtual environment
```
PS F:\gitrelease-py> .\venvps\Scripts\activate
(venvps) PS F:\gitrelease-py>
```

Test that the version of your virtual environment is correct
```
(venvps) PS F:\gitrelease-py> python -V
Python 3.8.2
```

Install dependencies
```
pip install pyinstaller click PyYAML requests
```

Build the distributable
```
pyinstaller --onefile -n gitrelease --hiddenimport click,requests,PyYAML main.py
```

You should see a bunch of output in your console and a single file (`gitrelease.exe`) in the `dist` folder
