#!/usr/bin/env jython

from kahuna.plugins.environment.infrastructure.network import cleanup_infrastructure_network
from kahuna.plugins.environment.infrastructure.storage import cleanup_infrastructure_storage
from com.abiquo.model.enumerator import *
from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.reference import *

class InfrastructureCompute:
    """ Provides access to infrastructure compute features. """
    
    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_datacenter(self, name, location):
        """ Creates a new datacenter. """
        print "Creating datacenter %s at %s..." % (name, location)
        rs_address = self.__context.getEndpoint().getHost()
        datacenter = Datacenter.builder(self.__context) \
                     .name(name) \
                     .location(location) \
                     .remoteServices(rs_address, AbiquoEdition.ENTERPRISE) \
                     .build()
        datacenter.save()
        return datacenter

    def create_rack(self, datacenter, name, vlan_id_min, vlan_id_max, nrsq):
        """ Creates a new rack. """
        print "Adding rack %s..." % name
        rack = Rack.builder(self.__context, datacenter) \
               .name(name) \
               .vlanIdMin(vlan_id_min) \
               .vlanIdMax(vlan_id_max) \
               .nrsq(nrsq) \
               .build()
        rack.save()
        return rack

    def create_machine(self, rack, hyp, address, user, password, datastore, vswitch):
        """ Creates a new machine. """
        print "Adding %s hypervisor at %s..." % (hyp, address)
        datacenter = rack.getDatacenter()

        # Discover machine info with the Discovery Manager remote service
        machine = datacenter.discoverSingleMachine(address, hyp, user, password)

        # Verify that the desired datastore and virtual switch exist
        datastore = machine.findDatastore(datastore)
        vswitch = machine.findAvailableVirtualSwitch(vswitch)

        datastore.setEnabled(True)
        machine.setVirtualSwitch(vswitch)
        machine.setRack(rack)

        machine.save()

        return machine

    #def create_machines(self, comp, rack):
	#""" Iterates machine creation. """
    #	for machine in MACHINES:
   	#    	comp.create_machine(rack, machine[0], machine[1], machine[2], machine[3], machine[4], machine[5])

def create_infrastructure_compute(config, context):
    """ Creates the default infrastructure compute entities using the plugin config values. """
    print "### Configuring infrastructure ###"
    comp = InfrastructureCompute(context)
    dc = comp.create_datacenter(config.get("datacenter", "name"),
            config.get("datacenter", "location"))
    rack = comp.create_rack(dc, config.get("rack", "name"),
            config.get("rack", "vlan-min"),
            config.get("rack", "vlan-max"),
            config.get("rack", "nrsq"))
    comp.create_machines(comp, rack,
            HypervisorType.valueOf(config.get("machine", "type"),
            config.get("machine", "address"),
            config.get("machine", "user"),
            config.get("machine", "password"),
            config.get("machine", "datastore"),
            config.get("machine", "vswitch"))
    return dc

def cleanup_infrastructure_compute(config, context):
    """ Cleans up previously created infrastructure compute resources. """
    print "### Cleaning up infrastructure ###"
    admin = context.getAdministrationService()
    for datacenter in admin.listDatacenters():
        cleanup_infrastructure_storage(config, datacenter)
        cleanup_infrastructure_network(config, datacenter)
        # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
        print "Removing datacenter %s..." % datacenter.getName()
        datacenter.delete()

