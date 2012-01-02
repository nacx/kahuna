#!/usr/bin/env jython

from abicli.constants import *
from abicli.infrastructure.network import cleanup_infrastructure_network
from abicli.infrastructure.storage import cleanup_infrastructure_storage
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

    def create_datacenter(self, name=DC_NAME, location=DC_LOCATION, rs_address=DC_ADDRESS):
        """ Creates a new datacenter.  

        If the parameters are not specified, the 'DC_NAME', 'DC_LOCATION'
        and 'DC_ADDRESS' variables from the 'constants' module will be used.
        """
        print "Creating datacenter %s at %s..." % (name, location)
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

def create_infrastructure_compute(context):
    """ Creates the standard infrastructure compute entities.
    
    Creates the standard infrastructure compute entities using the
    'constants' module properties.
    This is just an example of how to use this class.
    """
    print "### Configuring infrastructure ###"
    comp = InfrastructureCompute(context)
    dc = comp.create_datacenter()
    rack = comp.create_rack(dc)
    comp.create_machine(rack)
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

