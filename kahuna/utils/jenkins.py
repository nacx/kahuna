#!/usr/bin/env jython

from org.jclouds.scriptbuilder.domain import Statements

JENKINS = 'http://10.60.20.42'

def download_rs(version):
    script = []
    # TODO fix dependency from setupPublicCurl
    script.append(Statements.exec(
        "ensure_cmd_or_install_package_apt wget wget"))
    script.append(download_war(version, "am"))
    script.append(download_war(version, "bpm-async"))
    script.append(download_war(version, "nodecollector"))
    script.append(download_war(version, "ssm"))
    script.append(download_war(version, "virtualfactory"))
    script.append(download_war(version, "vsm.war"))
    script.append(download_script(version, "v2v-diskmanager",
        "/usr/local/bin"))
    script.append(download_script(version, "mechadora", "/usr/local/bin"))
    script.append(Statements.exec("chmod a+x /usr/local/bin/*"))
    return script


def download_war(version, file_name, destination="/tmp"):
    return Statements.exec("wget -O %s/%s.war %s/%s/%s.war" %
        (destination, file_name, JENKINS, version, file_name))


def download_script(version, file_name, destination="/tmp"):
    return Statements.exec("wget -O %s/%s %s/%s/scripts/%s" %
        (destination, file_name, JENKINS, version, file_name))
