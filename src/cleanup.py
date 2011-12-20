#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.predicates.cloud import *
from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *

def cleanup_virtual_appliance():
    print "Removing virtual appliancer %s..." % VAPP_NAME

    cloud = context.getCloudService()
    vdc = cloud.findVirtualDatacenter(VirtualDatacenterPredicates.name(VDC_NAME))
    vapp = vdc.findVirtualAppliance(VirtualAppliancePredicates.name(VAPP_NAME))
    vapp.delete()

def cleanup_virtual_datacenter():
    print "Removing virtual datacenter %s..." % VDC_NAME

    cloud = context.getCloudService()
    vdc = cloud.findVirtualDatacenter(VirtualDatacenterPredicates.name(VDC_NAME))
    vdc.delete()

def cleanup_tenants():
    print "Removing enterprise %s and all users..." % ENT_NAME
    admin = context.getAdministrationService()

    enterprise = admin.findEnterprise(EnterprisePredicates.name(ENT_NAME))

    # This will remove the enterprise and all users (if none of them is a Cloud Admin)
    enterprise.delete()

def cleanup_storage(datacenter):
    print "Removing storage_device %s..." % DEV_NAME
    device = datacenter.findStorageDevice(StorageDevicePredicates.name(DEV_NAME))
    device.delete()

def cleanup_infrastructure():
    admin = context.getAdministrationService()
    datacenter = admin.findDatacenter(DatacenterPredicates.name(DC_NAME))

    cleanup_storage(datacenter)

    # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
    print "Removing datacenter %s..." % DC_NAME
    datacenter.delete()


if __name__ == '__main__':

    # Context variable is initialised in config.py

    print "### Cleaning up the cloud ###"
    cleanup_virtual_appliance()
    cleanup_virtual_datacenter()
    print
    print "### Cleaning up tenants ###"
    cleanup_tenants()
    print
    print "### Cleaning up infrastructure ###"
    cleanup_infrastructure()

    # Close the connection to the Abiquo API
    context.close()

