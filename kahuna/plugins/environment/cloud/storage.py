#!/usr/bin/env jython

import logging
from org.jclouds.abiquo.domain.cloud import Volume
from org.jclouds.abiquo.predicates.infrastructure import TierPredicates

log = logging.getLogger('kahuna')


class CloudStorage:
    """ Provides access to cloud storage features """

    def __init__(self, context):
        """ Initialize the cloud creator with an existent context """
        self.__context = context

    def create_volume(self, vdc, tier, name, size):
        """ Creates a new volume in the given virtual datacenter """
        log.info("Creating volume %s of %s MB..." % (name, size))
        volume = Volume.builder(self.__context, vdc, tier) \
                 .name(name) \
                 .sizeInMb(size) \
                 .build()
        volume.save()
        return volume


def create_cloud_storage(config, context, vdc):
    """ Creates the default cloud storage entities """
    log.info("### Adding persistent storage ###")
    storage = CloudStorage(context)
    tier = vdc.findStorageTier(TierPredicates.name(config.get("tier", "name")))
    storage.create_volume(vdc, tier,
            config.get("volume", "name"),
            config.getint("volume", "size"))


def cleanup_cloud_storage(config, context, vdc):
    """ Cleans up a previously created cloud storage resources """
    log.info(("Removing persistent volumes in "
            "virtual datacenter %s...") % vdc.getName())
    for volume in vdc.listVolumes():
        volume.delete()
