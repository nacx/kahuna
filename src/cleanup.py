#!/usr/bin/env jython

from config import *
from constants import *

from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *


def cleanup_tenants(context):
    print "Removing enterprise %s and all users..." % ENT_NAME
    admin = context.getAdministrationService()

    enterprise = admin.findEnterprise(EnterprisePredicates.enterpriseName(ENT_NAME))

    # This will remove the enterprise and all users (if none of them is a Cloud Admin)
    enterprise.delete()

def cleanup_infrastructure(context):
    print "Removing datacenter %s..." % DC_NAME
    admin = context.getAdministrationService()
    
    datacenter = admin.findDatacenter(DatacenterPredicates.datacenterName(DC_NAME))

    # This will remove the datacenter and all hypervisors (if they don't contain deplopyed VMs)
    datacenter.delete()


if __name__ == '__main__':

    # Context variable is initialised in config.py

    cleanup_tenants(context)
    cleanup_infrastructure(context)

    # Close the connection to the Abiquo API
    context.close()

