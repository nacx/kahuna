#!/usr/bin/env jython

from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.predicates.infrastructure import *
from abicli.constants import *

class StorageCreator:
    """ Class that sets the methods for the storage entities.

    This class creates and manages all the 'storage' infrastructure
    elements of the cloud.
    """

    def __init__(self, loaded_context):
        """ Initialize with an existent context. """
        self.__context = loaded_context

    def configure_tiers(self, datacenter, tname=TIER_NAME):
        """ Configure the default Tiers of the datacenter. 

        It set a friendly name for a single tier and disables the rest.
        If the parameter 'tname' is not specified, it will use
        the 'TIER_NAME' from the 'constants' module.
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
        """ Discovers and registers a Storage Device.

        It discover a remote Storage Device and registers it into the
        specified datacenter. If parameters are not set, it will use the
        variables 'DEV_NAME', 'DEV_ADDRESS' and 'DEV_TYPE' from 'constants'
        module.
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

        Inside a StorageDevice and set as 'tier' parameter QoS, discovers
        and registers a storage pool. If parameter 'poolname' is not specified,
        it will use the 'POOL_NAME' variable from 'constants' module.
        """
        print "Adding pool %s..." % poolname
        pool = device.findRemoteStoragePool(StoragePoolPredicates.name(poolname))
        pool.setTier(tier)
        pool.save()
        return pool

def create_standard_storage(context, dc):
    """ Creates a standard storage entities.
    
    Creates a standard storage entities using the 'constants' module properties
    and is is useful as an example of how to use this class.
    """
    print "### Configuring storage ###"
    stor = StorageCreator(context)
    tier = stor.configure_tiers(dc)
    device = stor.create_device(dc)
    stor.create_pool(device, tier)

def cleanup_storage(datacenter):
    """ Cleans up a previously created standard storage entities. """
    print "Removing storage devices in datacenter %s..." % datacenter.getName()
    for device in datacenter.listStorageDevices():
        device.delete()
