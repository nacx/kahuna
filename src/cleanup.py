#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *


def cleanup_tenants(context):
    print "### Cleaning up tenants ###"
    print "Removing enterprise %s and all users..." % ENT_NAME
    admin = context.getAdministrationService()

    enterprise = admin.findEnterprise(EnterprisePredicates.enterpriseName(ENT_NAME))

    # This will remove the enterprise and all users (if none of them is a Cloud Admin)
    enterprise.delete()

def cleanup_storage(datacenter):
    print "Removing storage_device %s..." % DEV_NAME
    device = datacenter.findStorageDevice(StorageDevicePredicates.storageDeviceName(DEV_NAME))
    device.delete()

def cleanup_infrastructure(context):
    print "### Cleaning up infrastructure ###"
    admin = context.getAdministrationService()
    datacenter = admin.findDatacenter(DatacenterPredicates.datacenterName(DC_NAME))

    cleanup_storage(datacenter)

    # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
    print "Removing datacenter %s..." % DC_NAME
    datacenter.delete()


if __name__ == '__main__':

    # Context variable is initialised in config.py

    cleanup_tenants(context)
    print
    cleanup_infrastructure(context)

    # Close the connection to the Abiquo API
    context.close()

