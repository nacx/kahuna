#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.reference import *


def create_datacenter():
    print "Creating datacenter %s at %s..." % (DC_NAME, DC_ADDRESS)
    datacenter = Datacenter.builder(context) \
                 .name(DC_NAME) \
                 .location(DC_LOCATION) \
                 .remoteServices(DC_ADDRESS, AbiquoEdition.ENTERPRISE) \
                 .build()
    datacenter.save()
    return datacenter

def create_rack(datacenter):
    print "Adding rack %s..." % RACK_NAME
    rack = Rack.builder(context, datacenter) \
           .name(RACK_NAME) \
           .vlanIdMin(RACK_VLAN_MIN) \
           .vlanIdMax(RACK_VLAN_MAX) \
           .nrsq(RACK_NRSQ) \
           .build()
    rack.save()
    return rack

def create_machine(rack):
    print "Adding %s hypervisor at %s..." % (PM_TYPE, PM_ADDRESS)
    datacenter = rack.getDatacenter()

    # Discover machine info with the Discovery Manager remote service
    machine = datacenter.discoverSingleMachine(PM_ADDRESS, PM_TYPE, PM_USER, PM_PASSWORD)

    # Verify that the desired datastore and virtual switch exist
    datastore = machine.findDatastore(PM_DATASTORE)
    vswitch = machine.findAvailableVirtualSwitch(PM_VSWITCH)

    datastore.setEnabled(True)
    machine.setVirtualSwitch(vswitch)
    machine.setRack(rack)

    machine.save()

    return machine


if __name__ == '__main__':
    print "### Configuring infrastructure ###"

    # Context variable is initialised in config.py

    datacenter = create_datacenter()
    rack = create_rack(datacenter)
    machine = create_machine(rack)

    # Close the connection to the Abiquo API
    context.close()

