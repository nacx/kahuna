#!/usr/bin/env jython

from org.jclouds.scriptbuilder.domain import Statements

JENKINS = 'http://10.60.20.42'


# Before calling this function you may need to call
# Statements.call("setupPublicCurl")
def download_rs(version, destination="/tmp"):
    """ Downloads all Remote Services stuff from Jenkins """
    script = []
    script.append(Statements.exec(
        "ensure_cmd_or_install_package_apt wget wget"))
    script.append(_download_war(version, "am", destination))
    script.append(_download_war(version, "nodecollector", destination))
    script.append(_download_war(version, "ssm", destination))
    script.append(_download_war(version, "virtualfactory", destination))
    script.append(_download_war(version, "vsm", destination))
    script.extend(_download_bpm(version, destination))
    return script


def _download_war(version, file_name, destination="/tmp"):
    """ Downloads a given war from Jenkins """
    if file_name == "rs":
        return _download_rs(version)
    elif file_name == "bpm-async":
        return _download_bpm(version, destination)
    else:
        return [Statements.exec("wget -O %s/%s.war %s/%s/%s.war" %
            (destination, file_name, JENKINS, version, file_name))]


def _download_script(version, file_name, destination="/tmp"):
    """ Downloads the given script from Jenkins """
    return Statements.exec("wget -O %s/%s %s/%s/scripts/%s" %
        (destination, file_name, JENKINS, version, file_name))


def _download_database(version, destination="/tmp"):
    """ Downloads the given database from Jenkins """
    return Statements.exec("wget -O %s/kinton-schema-%s.sql "
        "%s/%s/database/kinton-schema.sql" %
        (destination, version, JENKINS, version))


def _download_bpm(version, destination="/tmp"):
    """ Downloads a given war from Jenkins """
    script = []
    script.append(_download_war(version, "bpm-async", destination))
    script.append(_download_script(version, "v2v-diskmanager",
        "/usr/local/bin"))
    script.append(_download_script(version, "mechadora", "/usr/local/bin"))
    script.append(Statements.exec("chmod a+x /usr/local/bin/*"))
    return script
