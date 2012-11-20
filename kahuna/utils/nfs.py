#!/usr/bin/env jython

from org.jclouds.scriptbuilder.domain import Statements


def mount(nfs_share, mount_point):
    """ Mounts a NFS in the given mount point """
    script = []
    script.append(Statements.exec("{md} %s" % mount_point))
    script.append(Statements.appendFile("/etc/fstab",
        ["%s %s nfs defaults 0 0" % (nfs_share, mount_point)]))
    script.append(Statements.exec("mount %s" % mount_point))
    return script
