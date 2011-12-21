#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.predicates.cloud import *
from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *


def cleanup_virtual_appliances(vdc):
    print "Removing virtual appliances in virtual datacenter %s..." % vdc.getName()
    for vapp in vdc.listVirtualAppliances():
        vapp.delete()

def cleanup_virtual_datacenter():
    cloud = context.getCloudService()
    for vdc in cloud.listVirtualDatacenters():
        cleanup_virtual_appliances(vdc)
        print "Removing virtual datacenter %s..." % vdc.getName()
        vdc.delete()

def cleanup_tenants():
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name(ENT_NAME))
    # This will remove the enterprise and all users (if none of them is a Cloud Admin)
    print "Removing enterprise %s and all users..." % enterprise.getName()
    enterprise.delete()

def cleanup_storage(datacenter):
    print "Removing storage devices in datacenter %s..." % datacenter.getName()
    for device in datacenter.listStorageDevices():
        device.delete()

def cleanup_infrastructure():
    admin = context.getAdministrationService()
    for datacenter in admin.listDatacenters():
        cleanup_storage(datacenter)
        # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
        print "Removing datacenter %s..." % datacenter.getName()
        datacenter.delete()


if __name__ == '__main__':

    # Context variable is initialised in config.py

    print "### Cleaning up the cloud ###"
    cleanup_virtual_datacenter()

    print "\n### Cleaning up tenants ###"
    cleanup_tenants()

    print "\n### Cleaning up infrastructure ###"
    cleanup_infrastructure()

    # Close the connection to the Abiquo API
    context.close()

