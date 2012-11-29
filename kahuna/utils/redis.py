#!/usr/bin/env jython

from java.net import URI
from org.jclouds.scriptbuilder.domain import Statements


# Before calling this function you may need to call
# Statements.call("setupPublicCurl")
def install(version):
    """ Downloads and installs redis """
    script = []
    script.append(Statements.exec("ensure_netutils_apt"))
    script.append(Statements.exec(
        "ensure_cmd_or_install_package_apt make build-essential"))
    script.append(Statements.extractTargzAndFlattenIntoDirectory(
        URI.create("http://redis.googlecode.com/files/redis-%s.tar.gz" %
            version),
        "/usr/local/src/redis"))
    script.append(Statements.exec(
        "(cd /usr/local/src/redis && make && make install)"))
    script.append(Statements.exec("{md} /var/lib/redis"))
    script.append(Statements.exec(
        "sed -i 's/^daemonize no/daemonize yes/' "
        "/usr/local/src/redis/redis.conf"))
    script.append(Statements.exec(
        "sed -i 's/^logfile .*/logfile \/var\/log\/redis.log/' "
        "/usr/local/src/redis/redis.conf"))
    script.append(Statements.exec(
        "sed -i 's/^dbfilename .*/dbfilename redis.rdb/' "
        "/usr/local/src/redis/redis.conf"))
    script.append(Statements.exec(
        "sed -i 's/^dir .*/dir \/var\/lib\/redis/' "
        "/usr/local/src/redis/redis.conf"))
    script.append(Statements.appendFile("/etc/sysctl.conf",
        ["vm.overcommit_memory = 1"]))
    script.append(Statements.exec(
        "/usr/local/bin/redis-server /usr/local/src/redis/redis.conf"))
    return script
