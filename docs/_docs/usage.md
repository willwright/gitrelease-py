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
  append
  checkout
  deploy
  feature
  init
  jira
  next
  prune
  rm
  roll
  status
(venv) will@PROWL:/mnt/f/gitrepo$
``` 

Help flags (`--help` or `-h`) are available on all commands for outputting additional information about each command.  

## append
Merge branches of a release branch *without* creating a new release candidate.

*Example*

Given that the current release branch checkout out is `release-v4.1.0-rc20`

Given that there are two branches in the current release
* origin/REPO-1
* origin/REPO-5

`append` will merge `origin/REPO-1` and `origin/REPO-5` into `release-v4.1.0-rc20` and then push to `origin`. Note that
the candidate (rc20) is *not* incremented.

## config
Set credentials for service integrations


## checkout
Checkout a specific release candidate

*Options*

`-b`, `--branches`
: option will list the branches in each release candidate

*Example*
```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py checkout -b
Fetching origin
Getting Release Branches...
  0: origin/release-v3.32.0-rc41
     --origin/bugfix/REPO-2660
     --origin/bugfix/REPO-3526
     --origin/feature/REPO-2430
     --origin/feature/REPO-3082
     --origin/feature/REPO-3087
     --origin/feature/REPO-3622-admin-RMA-changes
     --origin/bugfix/REPO-3570-adjust-can-creditmemo-method
     --origin/bugfix/REPO-3592-checkout-cartId-issue
     --origin/feature/REPO-3597
     --origin/bugfix/REPO-3613-free-shipping-code-admin
     --origin/bugfix/REPO-3564-fixing-rma-other-reason-processing
     --origin/feature/REPO-3349-refactor-giftcard-worker
     --origin/feature/REPO-3599
     --origin/feature/REPO-3629-add-columns-to-return-items-grid
     --origin/bugfix/REPO-3638
     --origin/bugfix/REPO-3572
     --origin/integration/REPO-3658
```

##deploy
Merge the current release candidate into the chosen ENVIRONMENT branch

*Arguments*

ENVIRONMENT
: the environment to merge the current releaes candidate into

*Options*

`-s`, `--squash`
: Use squash merge instead of recursive merge

## feature
Add a branch to the release.

*Arguments*

SEARCH
: Search branches haystack for the given SEARCH term

## init
Initialize a release. Creates all of the artifacts neccessary to use `gitrelease-py`.

This command can also be used to update any of the properties that are set. 

## jira
Updates JIRA with fixVersion for each branch in the current release or updates the current release with the issues from
JIRA.

*Arguments*

DIRECTION
 : *push* : Update JIRA issues with fixVersion
 : *pull* : Update local release with issues from JIRA

## next
Create a new release candidate by merging branches. Release candidate starts from current release candidate.

## prune
`prune` will prune the *current* version down to a specified number of release branches. The function will delete both local and
remote branches from all origins.

*Arguments*

KEEPBRANCHES

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
Remove a branch from the release.

If no search argument is provided the user will be given a list of branches to choose from.

*Example*

```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py rm
Branches found:
0: origin/bugfix/REPO-3498
1: origin/feature/REPO-3673-edi-import-lock
2: origin/bugfix/REPO-3669-fixing-wrong-clutch-bd-reward-amount-for-multi-shipping
3: origin/bugfix/REPO-3652
Select a branch to remove (x = cancel) [x]:
```

If a search argument is provided the list of branches will be filtered by the search term.

*Example*
```
(venv) will@PROWL:/mnt/f/gitrepo$ gitrelease-py rm 3673
Branches found:
0: origin/bugfix/REPO-3652
1: origin/bugfix/REPO-3498
2: origin/feature/REPO-3673-edi-import-lock <---
3: origin/bugfix/REPO-2660
4: origin/origin/bugfix/REPO-3430
5: origin/origin/bugfix/REPO-3353
6: origin/bugfix/REPO-2391-fixing-gift-card-add-twice-to-refund
Select a branch to remove (x = cancel) [2]:
Update JIRA fixVersion (y, n) [y]: n
Removed: origin/feature/REPO-3673-edi-import-lock

Master Branch: master
Staging Branch: staging
Development Branch: develop
Checked out Branch: release-v4.1.0-rc20

----------------------------------------------
Current Version: 4.1.0
Current Candidate: 20

Branches in this release:
origin/bugfix/REPO-3652
origin/bugfix/REPO-3498
origin/bugfix/REPO-2660
origin/origin/bugfix/REPO-3430
origin/origin/bugfix/REPO-3353
origin/bugfix/REPO-2391-fixing-gift-card-add-twice-to-refund
```

*Arguments*

SEARCH
: a needle to search for in branches haystack

## roll
Create a new release candidate by merging branches. Release candidate starts from master.

## status
Print out details about the current release candidate