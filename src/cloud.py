#!/usr/bin/env jython

from com.abiquo.model.enumerator import *

from com.apiclient.wrapper.admin import *
from com.apiclient.wrapper.cloud import *
from com.apiclient.connection import *


# Virtual datacenter configuration
VDC_NAME = "XS"
VDC_TYPE = HypervisorType.XENSERVER

# Network configuration
NET_NAME = "Default Network"
NET_ADDRESS = "192.168.1.0"
NET_MASK = 24
NET_GATEWAY = "192.168.1.1"

# Virtual appliance configuration
VAPP_NAME = "XS API"


def create_virtual_datacenter(datacenter, enterprise):
    net = VLANNetwork(NET_NAME, NET_ADDRESS, NET_MASK, NET_GATEWAY, True)
    vdc = VirtualDatacenter(datacenter, enterprise, VDC_NAME, VDC_TYPE, net)
    vdc.save()
    return vdc

def create_virtual_appliance(virtual_datacenter):
    vapp = VirtualAppliance(virtual_datacenter, VAPP_NAME)
    vapp.save()
    return vapp


def create_cloud():
    datacenter = ApiConnection.getConnection().getDatacenters()[0]
    enterprise = ApiConnection.getConnection().getEnterprises()[0]

    vdc = create_virtual_datacenter(datacenter, enterprise)
    create_virtual_appliance(vdc)


if __name__ == '__main__':
    create_cloud();

