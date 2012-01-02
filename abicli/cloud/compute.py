#!/usr/bin/env jython

from abicli.constants import *
from org.jclouds.abiquo.domain.cloud import *
from org.jclouds.abiquo.domain.network import *
from org.jclouds.abiquo.predicates.enterprise import *


class CloudCompute:
    """ Provides access to cloud compute features.

    This class creates and manages the compute resources of the cloud.
    """

    def __init__(self, context):
        """ Initialize the cloud creator with an existent context. """
        self.__context = context

    def create_virtual_datacenter(self, datacenter, enterprise, type, name=VDC_NAME, netname=NET_NAME, netaddress=NET_ADDRESS, netmask=NET_MASK, netgateway=NET_GATEWAY):
        """ Creates a new virtual datacenter. 

        If the parameters are not specified the 'VDC_NAME', 'NET_NAME',
        'NET_ADDRESS', 'NET_MASK' and 'NET_GATEWAY' variables from the
        'constants' module will be used.
        """
        print "Creating virtual datacenter %s of type %s..." % (name, type)
        network = PrivateNetwork.builder(self.__context) \
                  .name(netname) \
                  .address(netaddress) \
                  .mask(netmask) \
                  .gateway(netgateway) \
                  .build()
        vdc = VirtualDatacenter.builder(self.__context, datacenter, enterprise) \
              .name(name) \
              .hypervisorType(type) \
              .network(network) \
              .build()
        vdc.save()
        return vdc

    def create_virtual_appliance(self, vdc, name=VAPP_NAME):
        """ Creates a new virtual appliance inside a virtual datacenter.  

        If the parameter is not specified, the 'VAPP_NAME' variable
        from the 'constants' module will be used.
        """
        print "Creating virtual appliance %s..." % name
        vapp = VirtualAppliance.builder(self.__context, vdc) \
               .name(name) \
               .build()
        vapp.save()
        return vapp

    def refresh_template_repository(self, enterprise, datacenter):
        """ Refresh the virtual machines templates in the given repository. """
        print "Refreshing template repository..."
        enterprise.refreshTemplateRepository(datacenter)

def create_cloud_compute(context, dc):
    """ Creates the standard cloud compute entities.
    
    Creates the standard cloud compute entities using the 'constants'
    module properties.
    This is just an example of how to use this class.
    """
    print "### Configuring the cloud ###"
    cloud = CloudCompute(context)
    # Create it into the 'abiquo' enterprise, to make it easier to use
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name("Abiquo"))
    vdc = cloud.create_virtual_datacenter(dc, enterprise, PM_TYPE)
    cloud.create_virtual_appliance(vdc)
    cloud.refresh_template_repository(enterprise, dc)

def cleanup_cloud_compute(context):
    """ Cleans up a previously created cloud compute resources. """
    print "### Cleaning up the cloud ###"
    cloud = context.getCloudService()
    for virtualdc in cloud.listVirtualDatacenters():
        for virtualapp in virtualdc.listVirtualAppliances():
            virtualapp.delete()
        print "Removing virtual datacenter %s..." % virtualdc.getName()
        virtualdc.delete()

