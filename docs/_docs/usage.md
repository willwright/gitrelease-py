---
title: Usage
description: How to use gitrelease-py
---

# Usage

By default the main entry point of the application is `gitrelease-py`. 

## gitrelease-py
Running the script with no parameters will
result in a help dialog being outputted with the available sub-commands listed. 

**Example**
```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py
Usage: gitrelease-py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  checkout
  deploy
  feature
  init
  jirasync
  next
  prune
  rm
  roll
  status
(venv) will@PROWL:/mnt/f/gitrepo$
``` 

## checkout

## feature

## init

## jirasync

## next

## prune
`prune` will prune a version down to a specified number of release branches. The function will delete both local and
remote branches from all origins.

*Arguments*

keepbranches

: The number of branches to keep in the release history.

*Example*
Given a list of release branches for a version
```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py checkout
Fetching origin
Getting Release Branches...
  0: origin/release-v4.1.0-rc15
  1: origin/release-v4.1.0-rc16
  2: origin/release-v4.1.0-rc17
  3: origin/release-v4.1.0-rc18
  4: origin/release-v4.1.0-rc19
  5: origin/release-v4.1.0-rc20
```

Running `prune`
```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py prune 2
Fetching origin
Getting Release Branches...

release-v4.1.0-rc15
release-v4.1.0-rc16
release-v4.1.0-rc17
release-v4.1.0-rc18
The above branches are going to be permanently deleted; continue? [y/N]: y
Deleted branch release-v4.1.0-rc15 (was c0f8cf9be).

To https://github.com/willwright/gitrepo.git
 - [deleted]             release-v4.1.0-rc15

Deleted branch release-v4.1.0-rc16 (was 0a9acf306).

To https://github.com/willwright/gitrepo.git
 - [deleted]             release-v4.1.0-rc16

Deleted branch release-v4.1.0-rc17 (was 567d12343).

To https://github.com/willwright/gitrepo.git
 - [deleted]             release-v4.1.0-rc17

Deleted branch release-v4.1.0-rc18 (was 40c0026d9).

To https://github.com/willwright/gitrepo.git
 - [deleted]             release-v4.1.0-rc18


origin/release-v4.1.0-rc19
origin/release-v4.1.0-rc20
```

Results in 
```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py checkout
Fetching origin
Getting Release Branches...
  0: origin/release-v4.1.0-rc19
  1: origin/release-v4.1.0-rc20
```

## rm

## roll

## status