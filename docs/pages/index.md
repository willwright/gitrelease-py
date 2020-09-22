---
layout: page
title: gitrelease-py
permalink: /
---

# Welcome to gitrelease-py

## Purpose

`gitrelease-py` is a command line utility for managing release branches in git. It is meant to aid in the construction 
and management of ephemeral release branches. Branches can be added and removed, at will, from a release and the CLI 
will rebuild the release branch by iteratively merging the branches defined in the release. 

## Features Notes

**JIRA**

You *will* need a JIRA API Token in order to use the JIRA integration. [JIRA Documentation](https://confluence.atlassian.com/cloud/api-tokens-938839638.html)

**GITHUB**

You *will* need a GitHub Bearer token in order to use the GITHUB integration. [GitHub Documentation](https://github.com/settings/tokens)

**AWIGateway**

You *will* need API credentials to use the APIGateway.

## Contribute
Would you like to request a feature or contribute?
[Open an issue]({{ site.repo }}/issues)

## Examples
### Roll 
{% include gitgraph-roll.html %}

### Next
{% include gitgraph-next.html %}

### Append
{% include gitgraph-append.html %}