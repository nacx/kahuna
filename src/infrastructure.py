#!/usr/bin/env jython

from config import *

from com.abiquo.model.enumerator import *
from org.jclouds.abiquo.domain.infrastructure import *
from org.jclouds.abiquo.reference import *

# Datacenter configuration
DC_NAME = "Datacenter"
DC_LOCATION = "Honolulu"
DC_ADDRESS = "10.60.21.34"

# Rack configuration
RACK_NAME = "API rack"

# Machine configuration
PM_ADDRESS = "10.60.1.79"
PM_TYPE = HypervisorType.XENSERVER
PM_USER = "root"
PM_PASSWORD = "temporal"
PM_VSWITCH = "eth1"
PM_DATASTORE = "Local storage"


def create_datacenter(context):
    datacenter = Datacenter.builder(context) \
                 .name(DC_NAME) \
                 .location(DC_LOCATION) \
                 .remoteServices(DC_ADDRESS, AbiquoEdition.ENTERPRISE) \
                 .build()
    datacenter.save()
    return datacenter

def create_rack(datacenter):
    rack = Rack.builder(context, datacenter).name(RACK_NAME).build()
    rack.save()
    return rack

def create_machine(rack):
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

    # Context variable is initialised in config.py

    datacenter = create_datacenter(context)
    rack = create_rack(datacenter)
    machine = create_machine(rack)

    # Close the connection to the Abiquo API
    context.close()

