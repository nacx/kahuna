#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.predicates.infrastructure import *


def configure_tiers(datacenter):
    print "Enabling tier %s..." % TIER_NAME
    tiers = datacenter.listTiers()

    tiers[0].setName(TIER_NAME)
    tiers[0].update()

    for i in range(1, 4):
        tiers[i].setEnabled(False)
        tiers[i].update()

    return tiers[0]

def create_device(datacenter):
    print "Creating storage device %s at %s..." % (DEV_NAME, DEV_ADDRESS)
    device = StorageDevice.builder(context, datacenter) \
             .name(DEV_NAME) \
             .type(DEV_TYPE) \
             .iscsiIp(DEV_ADDRESS) \
             .managementIp(DEV_ADDRESS) \
             .build()
    device.save()
    return device


def create_pool(device, tier):
    print "Adding pool %s..." % POOL_NAME
    pool = device.findRemoteStoragePool(StoragePoolPredicates.storagePoolName(POOL_NAME))
    pool.setTier(tier)
    pool.save()
    return pool


if __name__ == '__main__':
    print "### Configuring storage ###"

    # Context variable is initialised in config.py

    admin = context.getAdministrationService()
    datacenter = admin.findDatacenter(DatacenterPredicates.datacenterName(DC_NAME))

    tier = configure_tiers(datacenter)
    device = create_device(datacenter)
    pool = create_pool(device, tier)

    # Close the connection to the Abiquo API
    context.close()

