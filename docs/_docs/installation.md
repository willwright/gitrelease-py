---
title: Installation
description: How to install gitrelease-py
---

# Installation
Distribution packages are made available for Mac and Windows.

## Latest

### Prerequisites
* git

### Mac
#### Git
Install Git
```
$ git --version
```

Test that git is locatable from the command line
```
➜  ~ git --version
git version 2.21.1 (Apple Git-122.3)
```

#### gitrelease
Download the latest executeable from the source below.

Run the executeable directly
 
```
➜  ~ ~/gitrelease/gitrelease
Usage: gitrelease [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  append    Merge branches to current release without incrementing releaese...
  checkout
  config    Set credentials for service integrations
  deploy    Merge the current release candidate into the chosen ENVIRONMENT...
  feature   Add a feature to the release.
  init      Initialize a release.
  jira      Updates the branches in this release from JIRA or updates JIRA...
  next      Create a new release candidate by merging branches.
  prune     Prune the number of release candidates in the current version...
  rm        Removes a branch from the release SEARCH: a needle to search
            for...

  roll      Create a new release candidate by merging branches.
  status    Print out details about the current release candidate
``` 

Or add the path to the installation directory to the PATH environment variable.
(Example assumes ZSH shell)

```
~ echo 'export PATH="$HOME/gitrelease:$PATH"' >> ~/.zshrc
```

```
➜  ~ gitrelease
Usage: gitrelease [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  append    Merge branches to current release without incrementing releaese...
  checkout
  config    Set credentials for service integrations
  deploy    Merge the current release candidate into the chosen ENVIRONMENT...
  feature   Add a feature to the release.
  init      Initialize a release.
  jira      Updates the branches in this release from JIRA or updates JIRA...
  next      Create a new release candidate by merging branches.
  prune     Prune the number of release candidates in the current version...
  rm        Removes a branch from the release SEARCH: a needle to search
            for...

  roll      Create a new release candidate by merging branches.
  status    Print out details about the current release candidate
```
 
### Windows
#### Git
Install Git [Git SCM](https://git-scm.com/download/)

When the installer runs choose "Git from the command line and also from 3rd-party software"

Test that git is locatable from the command line
```
PS C:\Users\Will> git --version
git version 2.26.0.windows.1
```
#### gitrelease
Download the latest executeable from the source below.

Run the executeable directly
 
 `PS C:\Users\Will\Downloads\gitrelease.exe`
 
 or add the path to the installation directory to the PATH environment variable.