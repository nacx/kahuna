#!/usr/bin/env jython
from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.reference import *
from abicli.constants import *
from abicli.infrastructure.storage import cleanup_storage

class ComputeCreator:
    """ Sets the methods for the infrastructure entities.

    This class creates and manages all the 'compute' elements
    of the cloud.
    """
    
    def __init__(self, loaded_context):
        """ Initialize with an existent context. """
        self.__context = loaded_context

    def create_datacenter(self, name=DC_NAME, location=DC_LOCATION, rs_address=DC_ADDRESS):
        """ Creates a new datacenter.  

        If the parameters are not specified, it will use the 
        'DC_NAME', 'DC_LOCATION' and 'DC_ADDRESS' from the 'constants' module.
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

        You must specify in which datacenter the rack will be created.
        If parameters are not informed, it will use the 'RACK_NAME', 'RACK_VLAN_MIN', 'RACK_VLAN_MAX',
        and 'RACK_NRSQ' values from 'constants' module.
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

        You must specify in whick Rack the machine is stored.
        If parameters are not informed, it will use the 'PM_TYPE', 'PM_ADDRESS', 'PM_USER', 
        'PM_PASSWORD','PM_DATASTORE','PM_SWITCH' from the 'constants' module.
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

def create_standard_compute(context):
    """ Creates a standard compute entities.
    
    Creates a standard compute entities using the 'constants' module properties
    and is is useful as an example of how to use this class.
    """
    print "### Configuring infrastructure ###"
    comp = ComputeCreator(context)
    dc = comp.create_datacenter()
    rack = comp.create_rack(dc)
    comp.create_machine(rack)
    return dc

def cleanup_infrastructure(context):
    """ Cleans up a previously created standard infrastructure. """
    print "\n### Cleaning up infrastructure ###"
    admin = context.getAdministrationService()
    for datacenter in admin.listDatacenters():
        cleanup_storage(datacenter)
        # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
        print "Removing datacenter %s..." % datacenter.getName()
        datacenter.delete()
