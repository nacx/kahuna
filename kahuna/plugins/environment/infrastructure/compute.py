#!/usr/bin/env jython

from kahuna.plugins.environment.constants import *
from kahuna.plugins.environment.infrastructure.network import cleanup_infrastructure_network
from kahuna.plugins.environment.infrastructure.storage import cleanup_infrastructure_storage
from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.reference import *


class InfrastructureCompute:
    """ Provides access to infrastructure compute features.

    This class creates and manages the compute elements
    of the infrastructure that will be exposed as a cloud.
    """
    
    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_datacenter(self, name=DC_NAME, location=DC_LOCATION):
        """ Creates a new datacenter.  

        If the parameters are not specified, the 'DC_NAME' and 'DC_LOCATION'
        variables from the 'constants' module will be used.
        """
        print "Creating datacenter %s at %s..." % (name, location)
        rs_address = self.__context.getEndpoint().getHost()
        datacenter = Datacenter.builder(self.__context) \
                     .name(name) \
                     .location(location) \
                     .remoteServices(rs_address, AbiquoEdition.ENTERPRISE) \
                     .build()
        datacenter.save()
        return datacenter

    def create_rack(self, datacenter, name=RACK_NAME, vlan_id_min=RACK_VLAN_MIN, vlan_id_max=RACK_VLAN_MAX, nrsq=RACK_NRSQ):
        """ Creates a new rack.

        You must specify the datacenter where the rack will be created.
        If parameters are not specified, the 'RACK_NAME', 'RACK_VLAN_MIN',
        'RACK_VLAN_MAX', and 'RACK_NRSQ' variables from the 'constants'
        module will be used.
        """
        print "Adding rack %s..." % name
        rack = Rack.builder(self.__context, datacenter) \
               .name(name) \
               .vlanIdMin(vlan_id_min) \
               .vlanIdMax(vlan_id_max) \
               .nrsq(nrsq) \
               .build()
        rack.save()
        return rack

    def create_machine(self, rack, hyp=PM_TYPE, address=PM_ADDRESS, user=PM_USER, password=PM_PASSWORD, datastore=PM_DATASTORE, vswitch=PM_VSWITCH):
        """ Creates a new machine.

        You must specify the rack where the machine will be created.
        If parameters are not informed, the 'PM_TYPE', 'PM_ADDRESS',
        'PM_USER', 'PM_PASSWORD', 'PM_DATASTORE' and 'PM_SWITCH'
        variables from the 'constants' module will be used.
        """
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

    def create_machines(self, comp, rack):
	""" Iterates machine creation
	"""
	
	print "Adding physical machines"
	for machine in MACHINES:
   		comp.create_machine(rack, machine[0], machine[1], machine[2], machine[3], machine[4], machine[5])

def create_infrastructure_compute(context):
    """ Creates the default infrastructure compute entities.
    
    Creates the default infrastructure compute entities using the
    'constants' module properties.
    This is just an example of how to use this class.
    """
    print "### Configuring infrastructure ###"
    comp = InfrastructureCompute(context)
    dc = comp.create_datacenter()
    rack = comp.create_rack(dc)
    comp.create_machines(comp, rack)
    return dc

def cleanup_infrastructure_compute(context):
    """ Cleans up previously created infrastructure compute resources. """
    print "### Cleaning up infrastructure ###"
    admin = context.getAdministrationService()
    for datacenter in admin.listDatacenters():
        cleanup_infrastructure_storage(datacenter)
        cleanup_infrastructure_network(datacenter)
        # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
        print "Removing datacenter %s..." % datacenter.getName()
        datacenter.delete()

