#!/usr/bin/env jython

import logging
import os
from java.io import File
from org.jclouds.io import Payloads
from org.jclouds.util import Strings2

log = logging.getLogger('kahuna')


def get(context, node, file):
    """ Get the contents of a file in a remote host """
    ssh = context.getUtils().sshForNode().apply(node)
    try:
        ssh.connect()
        payload = ssh.get(file)
        return Strings2.toStringAndClose(payload.getInput())
    finally:
        if payload:
            payload.release()
        if ssh:
            ssh.disconnect()


def upload(context, node, directory, filepath):
    """ Upload a file to a host """
    log.info("Waiting for ssh access on node %s..." % node.getName())
    ssh = context.getUtils().sshForNode().apply(node)
    filename = os.path.basename(filepath)
    file = File(filepath)
    try:
        log.info("Uploading %s to %s..." % (filename, node.getName()))
        ssh.connect()
        ssh.put(directory + "/" + filename, Payloads.newFilePayload(file))
    finally:
        if ssh:
            ssh.disconnect()
