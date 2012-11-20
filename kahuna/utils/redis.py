#!/usr/bin/env jython

from java.net import URI
from org.jclouds.scriptbuilder.domain import Statements


def install():
    script = []
    # TODO fix dependency from setupPublicCurl
    script.append(Statements.exec("ensure_netutils_apt"))
    script.append(Statements.exec(
        "ensure_cmd_or_install_package_apt make build-essential"))
    script.append(Statements.extractTargzAndFlattenIntoDirectory(
        URI.create("http://redis.googlecode.com/files/redis-2.6.4.tar.gz"),
        "/usr/local/src/redis"))
    script.append(Statements.exec(
        "( cd /usr/local/src/redis && make && make install )"))
    script.append(Statements.exec(
        "sed -i 's/^daemonize no/daemonize yes/' "
        "/usr/local/src/redis/redis.conf"))
    script.append(Statements.exec(
        "/usr/local/bin/redis-server /usr/local/src/redis/redis.conf"))
    return script
