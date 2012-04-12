#!/usr/bin/env jython

import logging
from ConfigParser import NoOptionError
from com.abiquo.model.enumerator import StorageTechnologyType
from org.jclouds.abiquo.domain.infrastructure import StorageDevice
from org.jclouds.abiquo.predicates.infrastructure import StoragePoolPredicates

log = logging.getLogger('kahuna')


class InfrastructureStorage:
    """ Provides access to infrastructure storage features. """

    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context.getProviderSpecificContext()

    def configure_tiers(self, datacenter, tier):
        """ Configure the default tiers of the datacenter. """
        log.info("Enabling tier %s..." % tier)
        tiers = datacenter.listTiers()

        tiers[0].setName(tier)
        tiers[0].update()

        for tier in tiers[1:]:
            tier.setEnabled(False)
            tier.update()

        return tiers[0]

    def create_device(self, datacenter, devname, devtype, devaddress,
            devmanaddress, user, password):
        """ Discovers and registers a storage device. """
        log.info("Creating storage device %s at %s..." % (devname,
            devaddress))
        device = StorageDevice.builder(self.__context, datacenter) \
                 .name(devname) \
                 .type(devtype) \
                 .iscsiIp(devaddress) \
                 .managementIp(devmanaddress) \
                 .username(user) \
                 .password(password) \
                 .build()
        device.save()
        return device

    def create_pool(self, device, tier, poolname):
        """ Discovers and registers a StoragePool. """
        log.info("Adding pool %s..." % poolname)
        pool = device.findRemoteStoragePool(
            StoragePoolPredicates.name(poolname))
        pool.setTier(tier)
        pool.save()
        return pool


def create_infrastructure_storage(config, context, dc):
    """ Creates the default infrastructure storage entities. """
    log.info("### Configuring storage ###")
    storage = InfrastructureStorage(context)
    tier = storage.configure_tiers(dc, config.get("tier", "name"))
    try:
        user = config.get("device", "user")
        password = config.get("device", "password")
    except NoOptionError:
        user = None
        password = None
    device = storage.create_device(dc, config.get("device", "name"),
        StorageTechnologyType.valueOf(config.get("device", "type")),
        config.get("device", "address"),
        config.get("device", "address"),
        user, password)

    storage.create_pool(device, tier, config.get("pool", "name"))


def cleanup_infrastructure_storage(config, datacenter):
    """ Cleans up previously created infrastructure storage entities. """
    log.info(("Removing storage devices in "
            "datacenter %s...") % datacenter.getName())
    for device in datacenter.listStorageDevices():
        device.delete()
