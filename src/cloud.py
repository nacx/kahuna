#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.domain.cloud import *
from org.jclouds.abiquo.domain.network import *
from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *


def create_virtual_datacenter(datacenter, enterprise, type):
    print "Creating virtual datacenter %s of type %s..." % (VDC_NAME, type)
    network = PrivateNetwork.builder(context) \
              .name(NET_NAME) \
              .address(NET_ADDRESS) \
              .mask(NET_MASK) \
              .gateway(NET_GATEWAY) \
              .build()

    vdc = VirtualDatacenter.builder(context, datacenter, enterprise) \
          .name(VDC_NAME) \
          .hypervisorType(type) \
          .network(network) \
          .build()

    vdc.save()

    return vdc

def create_virtual_appliance(vdc):
    print "Creating virtual appliance %s..." % VAPP_NAME
    vapp = VirtualAppliance.builder(context, vdc) \
           .name(VAPP_NAME) \
           .build()
    vapp.save()

    return vapp

def refresh_template_repository(enterprise, datacenter):
    print "Refreshing template repository..."
    enterprise.refreshTemplateRepository(datacenter)

if __name__ == '__main__':
    print "### Configuring the cloud ###"

    # Context variable is initialised in config.py

    admin = context.getAdministrationService()
    datacenter = admin.findDatacenter(DatacenterPredicates.name(DC_NAME))
    enterprise = admin.findEnterprise(EnterprisePredicates.name(VDC_ENTERPRISE))

    vdc = create_virtual_datacenter(datacenter, enterprise, PM_TYPE)
    vapp = create_virtual_appliance(vdc)
    refresh_template_repository(enterprise, datacenter)

    # Close the connection to the Abiquo API
    context.close()

