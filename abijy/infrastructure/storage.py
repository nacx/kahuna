#!/usr/bin/env jython

from abijy.constants import *
from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.predicates.infrastructure import *


class InfrastructureStorage:
    """ Provides access to infrastructure storage features.

    This class creates and manages the storage resources of the
    infrastructure that will be exposed as a cloud.
    """

    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def configure_tiers(self, datacenter, tname=TIER_NAME):
        """ Configure the default tiers of the datacenter. 

        It sets af riendly name for the first tier and disables the rest.
        If the parameter 'tname' is not specified, the 'TIER_NAME' variable
        from the 'constants' module will be used.
        """
        print "Enabling tier %s..." % tname 
        tiers = datacenter.listTiers()

        tiers[0].setName(tname)
        tiers[0].update()

        for i in range(1, 4):
            tiers[i].setEnabled(False)
            tiers[i].update()

        return tiers[0]

    def create_device(self, datacenter, devname=DEV_NAME, devtype=DEV_TYPE,devaddress=DEV_ADDRESS, devmanaddress=DEV_ADDRESS):
        """ Discovers and registers a storage device.

        It discovers a remote storage device and registers it into the
        given datacenter. If parameters are not set, the 'DEV_NAME',
        'DEV_ADDRESS' and 'DEV_TYPE' variables from the 'constants'
        module will be used.
        """
        print "Creating storage device %s at %s..." % (devname, devaddress)
        device = StorageDevice.builder(self.__context, datacenter) \
                 .name(devname) \
                 .type(devtype) \
                 .iscsiIp(devaddress) \
                 .managementIp(devmanaddress) \
                 .build()
        device.save()
        return device

    def create_pool(self, device, tier, poolname=POOL_NAME): 
        """ Discovers and registers a StoragePool.

        Discovers the information of the given pool from the given
        storage device, and adds it to the given tier.
        If parameter 'poolname' is not specified, the 'POOL_NAME'
        variable from the 'constants' module will be used.
        """
        print "Adding pool %s..." % poolname
        pool = device.findRemoteStoragePool(StoragePoolPredicates.name(poolname))
        pool.setTier(tier)
        pool.save()
        return pool

def create_infrastructure_storage(context, dc):
    """ Creates the default infrastructure storage entities.
    
    Creates the default infrastructure storage entities using
    the 'constants' module properties.
    This is just an example of how to use this class.
    """
    print "### Configuring storage ###"
    storage = InfrastructureStorage(context)
    tier = storage.configure_tiers(dc)
    device = storage.create_device(dc)
    storage.create_pool(device, tier)

def cleanup_infrastructure_storage(datacenter):
    """ Cleans up previously created infrastructure storage entities. """
    print "Removing storage devices in datacenter %s..." % datacenter.getName()
    for device in datacenter.listStorageDevices():
        device.delete()

