#!/usr/bin/env jython

from org.jclouds.scriptbuilder.domain import Statements


def configure(node):
    """ Generates the script to set the hostname in a node """
    script = []
    script.append(Statements.exec("hostname %s" % node.getName()))
    script.append(Statements.createOrOverwriteFile(
        "/etc/hostname", [node.getName()]))
    script.append(Statements.exec(
        "sed -i 's/127.0.0.1/127.0.0.1\t%s/' /etc/hosts" % node.getName()))
    return script
