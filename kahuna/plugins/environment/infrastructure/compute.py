#!/usr/bin/env jython

import logging
from kahuna.plugins.environment.infrastructure.network import cleanup_infrastructure_network
from kahuna.plugins.environment.infrastructure.storage import cleanup_infrastructure_storage
from com.abiquo.model.enumerator import HypervisorType
from org.jclouds.abiquo.config import AbiquoEdition
from org.jclouds.abiquo.domain.infrastructure import Datacenter
from org.jclouds.abiquo.domain.infrastructure import Rack

log = logging.getLogger('kahuna')


class InfrastructureCompute:
    """ Provides access to infrastructure compute features """

    def __init__(self, context):
        """ Initialize with an existent context """
        self.__context = context.getApiContext()

    def create_datacenter(self, name, location, rs_address):
        """ Creates a new datacenter """
        log.info("Creating datacenter %s at %s..." % (name, location))
        datacenter = Datacenter.builder(self.__context) \
                     .name(name) \
                     .location(location) \
                     .remoteServices(rs_address, AbiquoEdition.ENTERPRISE) \
                     .build()
        datacenter.save()
        return datacenter

    def create_rack(self, datacenter, name, vlan_id_min, vlan_id_max, nrsq):
        """ Creates a new rack """
        log.info("Adding rack %s..." % name)
        rack = Rack.builder(self.__context, datacenter) \
               .name(name) \
               .vlanIdMin(vlan_id_min) \
               .vlanIdMax(vlan_id_max) \
               .nrsq(nrsq) \
               .build()
        rack.save()
        return rack

    def create_machine(self, rack, hyp, address, user, password,
            datastore, vswitch):
        """ Creates a new machine """
        log.info("Adding %s hypervisor at %s..." % (hyp, address))
        datacenter = rack.getDatacenter()

        # Discover machine info with the Discovery Manager remote service
        machine = datacenter.discoverSingleMachine(address, hyp,
                user, password)
        for ds in machine.getDatastores():
            log.debug("Datastore found: %s-%s" %
                    (ds.getName(), ds.getRootPath()))

        # Verify that the desired datastore and virtual switch exist
        datastore = machine.findDatastore(datastore)
        vswitch = machine.findAvailableVirtualSwitch(vswitch)

        datastore.setEnabled(True)
        machine.setVirtualSwitch(vswitch)
        machine.setRack(rack)

        machine.save()

        return machine


def create_infrastructure_compute(config, context):
    """ Creates the default infrastructure compute entities. """
    log.info("### Configuring infrastructure ###")
    comp = InfrastructureCompute(context)
    rs_address = config.get("datacenter", "rs") \
            if config.has_option("datacenter", "rs") \
            else context.getApiContext().getEndpoint().getHost()
    dc = comp.create_datacenter(config.get("datacenter", "name"),
            config.get("datacenter", "location"), rs_address)
    rack = comp.create_rack(dc, config.get("rack", "name"),
            config.getint("rack", "vlan-min"),
            config.getint("rack", "vlan-max"),
            config.getint("rack", "nrsq"))

    sections = filter(lambda s: s.startswith("machine"), config.sections())
    for section in sections:
        comp.create_machine(rack,
                HypervisorType.valueOf(config.get(section, "type")),
                config.get(section, "address"),
                config.get(section, "user"),
                config.get(section, "password"),
                config.get(section, "datastore"),
                config.get(section, "vswitch"))
    return dc


def cleanup_infrastructure_compute(config, context):
    """ Cleans up previously created infrastructure compute resources """
    log.info("### Cleaning up infrastructure ###")
    admin = context.getAdministrationService()
    for datacenter in admin.listDatacenters():
        cleanup_infrastructure_storage(config, datacenter)
        cleanup_infrastructure_network(config, datacenter)
        # This will remove the datacenter and all hypervisors
        # (if they don't contain deplopyed VMs)
        log.info("Removing datacenter %s..." % datacenter.getName())
        datacenter.delete()
