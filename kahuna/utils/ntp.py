#!/usr/bin/env jython

from org.jclouds.scriptbuilder.domain import Statements


# Before calling this function you may need to call
# Statements.call("setupPublicCurl")
def install():
    """ Downloads and installs the NTP daemon """
    return Statements.exec(
        "ensure_cmd_or_install_package_apt ntpd ntp")
