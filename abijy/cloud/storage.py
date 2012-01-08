#!/usr/bin/env jython

from abijy.constants import *
from org.jclouds.abiquo.domain.cloud import *
from org.jclouds.abiquo.predicates.cloud import *
from org.jclouds.abiquo.predicates.infrastructure import *


class CloudStorage:
    """ Provides access to cloud storage features.

    This class creates and manages the storage resources of the cloud.
    """

    def __init__(self, context):
        """ Initialize the cloud creator with an existent context. """
        self.__context = context

    def create_volume(self, vdc, tier, name=VOL_NAME, size=VOL_SIZE):
        """ Creates a new volume in the given virtual datacenter. 

        If the parameters are not specified the 'VOL_NAME' and 'VOL_SIZE',
        variables from the 'constants' module will be used.
        """
        print "Creating volume %s of %s MB..." % (name, size)
        volume = Volume.builder(self.__context, vdc, tier) \
                 .name(name) \
                 .sizeInMb(size) \
                 .build()
        volume.save()
        return volume

def create_cloud_storage(context, vdc):
    """ Creates the default cloud storage entities.
    
    Creates the default cloud storage entities using the 'constants'
    module properties.
    This is just an example of how to use this class.
    """
    print "### Adding persistent storage ###"
    storage = CloudStorage(context)
    tier = vdc.findStorageTier(TierPredicates.name(TIER_NAME))
    storage.create_volume(vdc, tier)

def cleanup_cloud_storage(context, vdc):
    """ Cleans up a previously created cloud storage resources. """
    print "Removing persistent volumes in virtual datacenter %s..." % vdc.getName()
    for volume in vdc.listVolumes():
        volume.delete()

