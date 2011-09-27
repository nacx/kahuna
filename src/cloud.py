#!/usr/bin/env jython

from com.abiquo.model.enumerator import *

from com.apiclient.wrapper.infrastructure import *
from com.apiclient.wrapper.network import *
from com.apiclient.wrapper.enterprise import *
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

# External storage configuration
VOL_NAME = "Ext. Storage"
VOL_SIZE = 1024     # GB
VOL_TIER = "Default Tier 1"


def create_virtual_datacenter(datacenter, enterprise):
    net = VLANNetwork(NET_NAME, NET_ADDRESS, NET_MASK, NET_GATEWAY, True)
    vdc = VirtualDatacenter(datacenter, enterprise, VDC_NAME, VDC_TYPE, net)
    vdc.save()
    return vdc

def create_virtual_appliance(virtual_datacenter):
    vapp = VirtualAppliance(virtual_datacenter, VAPP_NAME)
    vapp.save()
    return vapp

def create_volume(vdc, tier):
    volume = Volume(VOL_NAME, VOL_SIZE, vdc, tier)
    volume.save()
    return volume


if __name__ == '__main__':
    datacenter = Admin.getDatacenters()[0]
    enterprise = Admin.getEnterprises()[0]

    vdc = create_virtual_datacenter(datacenter, enterprise)
    vapp = create_virtual_appliance(vdc)

    tier = filter(lambda t: t.getName() == VOL_TIER, datacenter.getTiers())[0]
    volume = create_volume(vdc, tier)

