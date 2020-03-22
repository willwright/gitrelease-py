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

## Features

 - Add and remove branches by searching branch tree
 - JIRA integration
 - Roll release from master or from previous release candidate


For features, getting started with development, see the {% include doc.html name="Getting Started" path="getting-started" %} page. Would you like to request a feature or contribute?
[Open an issue]({{ site.repo }}/issues)