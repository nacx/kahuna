#!/usr/bin/env jython

from com.abiquo.model.enumerator import *

from com.apiclient.wrapper.infrastructure import *
from com.apiclient.wrapper.enterprise import *
from com.apiclient.connection.constants import *


# Datacenter configuration
DC_NAME = "Datacenter"
DC_LOCATION = "Honolulu"
DC_ADDRESS = "10.60.1.222"

# Machine configuration
PM_ADDRESS = "10.60.1.79"
PM_TYPE = HypervisorType.XENSERVER
PM_USER = "root"
PM_PASSWORD = "temporal"
PM_VIRTUALSWITCH = "eth1"
PM_DATASTORE = "Local storage"


def create_datacenter():
    datacenter = Datacenter(DC_NAME, DC_LOCATION, DC_ADDRESS, AbiquoKeyWords.AbiquoEdition.ENTERPRISE)
    datacenter.save()
    return datacenter

def create_rack(datacenter):
    rack = Rack(datacenter, "Rack", "", False)
    rack.save()
    return rack

def create_machine(rack):
    datacenter = rack.getDatacenter()
    machine = datacenter.getRemoteMachine(PM_ADDRESS, PM_TYPE, PM_USER, PM_PASSWORD)

    virtual_switch = filter(lambda vs: vs == PM_VIRTUALSWITCH, machine.getVirtualSwitches())[0]
    datastore = filter(lambda ds: ds.getName() == PM_DATASTORE, machine.getAllDatastores())[0]
    datastore.setEnabled(True)

    machine.setRack(rack)
    machine.setVirtualSwitch(virtual_switch)
    machine.save()

    return machine


if __name__ == '__main__':
    datacenter = create_datacenter()
    rack = create_rack(datacenter)
    machine = create_machine(rack)

