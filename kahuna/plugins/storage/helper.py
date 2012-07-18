#!/usr/bin/env jython

import logging
from org.jclouds.abiquo.predicates.cloud import VirtualMachinePredicates
from org.jclouds.abiquo.predicates.cloud import VolumePredicates

log = logging.getLogger('kahuna')


def find_volume(context, name):
    """ Find a volume given its name """
    cloud = context.getCloudService()
    vdcs = cloud.listVirtualDatacenters()
    log.debug("Looking for volume: %s" % name)
    for vdc in vdcs:
        volume = vdc.findVolume(VolumePredicates.name(name))
        if volume:
            log.debug("Found volume in virtual datacenter: %s" % vdc.getName())
            return volume


def refresh_volume(context, volume):
    """ Refresh the given volume """
    vdc = volume.getVirtualDatacenter()
    return vdc.getVolume(volume.getId())


def get_attached_vm(context, volume):
    """ Get the virtual machine where the volume is attached """
    # TODO: Add parent navigation in jclouds.abiquo
    link = volume.unwrap().searchLink("virtualmachine")
    if link:
        name = link.getTitle()
        cloud = context.getCloudService()
        return cloud.findVirtualMachine(VirtualMachinePredicates.internalName(name))
