---
title: Installation
description: How to install gitrelease-py
---

# Installation
Distribution packages are made available for Mac, Ubuntu, and Windows.

## Latest
Mac: [gitrelease-1.0.0](https://gitrelease-py.s3-us-west-1.amazonaws.com/mac/1.0.0/gitrelease)

Ubuntu: [gitrelease-1.0.0](https://gitrelease-py.s3-us-west-1.amazonaws.com/ubuntu/1.0.0/gitrelease)

Windows: [gitrelease-1.0.0](https://gitrelease-py.s3-us-west-1.amazonaws.com/windows/1.0.0/gitrelease.exe)

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
Download the latest executable from the source above.

Run the executable directly
 
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
 
### WSL (Windows Linux Sub-System) - Ubuntu
#### Git
Install Git

```
apt-get install git
```

Test that git is locatable from the command line
```
will@PROWL:~$ git --version
git version 2.17.1
```
#### gitrelease
Download the latest executable from the source above.

Run the executable directly
```
(venv) will@PROWL:~$ gitrelease
Usage: gitrelease-py [OPTIONS] COMMAND [ARGS]...

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
Download the latest executable from the source above.

Run the executable directly
 
`PS C:\Users\Will\gitrelease\gitrelease.exe`
 
Or add the path to the installation directory to the PATH environment variable.

Press windows key and search for "environment"

Choose "Edit the System Environment"

![Environment]({{ site.baseurl }}/assets/img/installation/environment.png)

Choose Environment Variables...

Choose Path

Click Edit...

![Path]({{ site.baseurl }}/assets/img/installation/path.png)

Click New

Add you're installation directory

![Edit Path]({{ site.baseurl }}/assets/img/installation/edit-path.png)

Click OK

Test that the application is available from the terminal

```
PS C:\Users\Will> gitrelease
Usage: gitrelease.exe [OPTIONS] COMMAND [ARGS]...

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