#!/usr/bin/env jython

from org.jclouds.scriptbuilder.statements.git import CloneGitRepo
from org.jclouds.scriptbuilder.statements.git import InstallGit


def install():
    """ Generates the Git install script """
    return InstallGit()


def clone(repo, directory, branch="master"):
    """ Clones a git repository """
    return CloneGitRepo.builder() \
        .repository(repo) \
        .branch(branch) \
        .directory(directory) \
        .build()


def clone_opscode_cookbook(cookbook):
    """ Clone a cookbook from teh opscode cookbooks repository """
    return clone("git://github.com/opscode-cookbooks/%s.git" % cookbook,
                 "/var/chef/cookbooks/%s" % cookbook)
