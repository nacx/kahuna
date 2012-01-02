#!/usr/bin/env jython
from org.jclouds.abiquo.domain.cloud import *
from org.jclouds.abiquo.domain.network import *
from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *
from abicli.constants import *

class CloudCreator:
    """ Sets the methods for the cloud entities.

    This class creates and manages all the 'cloud' elements
    of the cloud.
    """

    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_virtual_datacenter(self, datacenter, enterprise, type, name=VDC_NAME, netname=NET_NAME, netaddress=NET_ADDRESS, netmask=NET_MASK, netgateway=NET_GATEWAY):
        """ Creates a new Virtual Datacenter. 

        If the parameters are not specified it will use the 'VDC_NAME',
        'NET_NAME', 'NET_ADDRESS', 'NET_MASK', 'NET_GATEWAY' from
        the 'constants' module
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
        """ Creates a new virtualappliance inside a virtual datacenter.  
        If the parameter is not specified, it will use the 'VAPP_NAME' variable
        from the 'constants' module.
        """
        print "Creating virtual appliance %s..." % name
        vapp = VirtualAppliance.builder(self.__context, vdc) \
               .name(name) \
               .build()
        vapp.save()

        return vapp

    def refresh_template_repository(self, enterprise, datacenter):
        """ Calls the AM to refresh the template repository. """
        print "Refreshing template repository..."
        enterprise.refreshTemplateRepository(datacenter)

def create_standard_cloud(context, dc):
    """ Creates a standard cloud entities.
    
    Creates a standard cloud entities using the 'constants' module properties
    and is is useful as an example of how to use this class.
    """
    print "### Configuring the cloud ###"
    cloud = CloudCreator(context)
    # we create it into 'abiquo' enterprise since we want to delete if after all
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name("Abiquo"))
    vdc = cloud.create_virtual_datacenter(dc, enterprise, PM_TYPE)
    cloud.create_virtual_appliance(vdc)
    cloud.refresh_template_repository(enterprise, dc)

def cleanup_cloud(context):
    """ Cleans up a previously created cloud infrastructure. """
    print "### Cleaning up the cloud ###"
    cloud = context.getCloudService()
    for virtualdc in cloud.listVirtualDatacenters():
        for virtualapp in virtualdc.listVirtualAppliances():
            virtualapp.delete()
        print "Removing virtual datacenter %s..." % virtualdc.getName()
        virtualdc.delete()
