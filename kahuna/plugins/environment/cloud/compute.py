#!/usr/bin/env jython

from kahuna.plugins.environment.cloud.storage import cleanup_cloud_storage
from com.abiquo.model.enumerator import *
from org.jclouds.abiquo.domain.cloud import *
from org.jclouds.abiquo.domain.network import *
from org.jclouds.abiquo.predicates.enterprise import *

class CloudCompute:
    """ Provides access to cloud compute features. """

    def __init__(self, context):
        """ Initialize the cloud creator with an existent context. """
        self.__context = context

    def create_virtual_datacenter(self, datacenter, enterprise, type,
            name, netname, netaddress, netmask, netgateway):
        """ Creates a new virtual datacenter. """
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

    def create_virtual_appliance(self, vdc, name):
        """ Creates a new virtual appliance inside a virtual datacenter. """ 
        print "Creating virtual appliance %s..." % name
        vapp = VirtualAppliance.builder(self.__context, vdc) \
               .name(name) \
               .build()
        vapp.save()
        return vapp

    def create_virtual_machine(self, vapp, template):
        """ Create a virtual machine based on the given template. """
        print "Creating virtual machine from template: %s..." % template.getName()
        vm = VirtualMachine.builder(self.__context, vapp, template).build()
        vm.save()
        return vm

    def refresh_template_repository(self, enterprise, datacenter):
        """ Refresh the virtual machines templates in the given repository. """
        print "Refreshing template repository..."
        enterprise.refreshTemplateRepository(datacenter)

def find_smallest_template(context, vdc):
    """ Finds the smallest template available to the given virtual datacenter. """
    print "Looking for the smallest available template..."
    templates = sorted(vdc.listAvailableTemplates(), key=lambda t: t.getDiskFileSize())
    if len(templates) > 0:
        print "Found compatible template: %s" % templates[0].getName()
        return templates[0]
    else:
        print "No compatible template found"
        return None

def create_cloud_compute(config, context, dc):
    """ Creates the default cloud compute entities using the plugin config values. """
    print "### Configuring the cloud ###"
    cloud = CloudCompute(context)
    # Create it into the 'abiquo' enterprise, to make it easier to use
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name("Abiquo"))
    vdc = cloud.create_virtual_datacenter(dc, enterprise,
            HypervisorType.valueOf(config.get("machine", "type")),
            config.get("virtual datacenter", "name"),
            config.get("private network", "name"),
            config.get("private network", "address"),
            config.getint("private network", "mask"),
            config.get("private network", "gateway"))
    vapp = cloud.create_virtual_appliance(vdc, config.get("virtual appliance", "name"))
    cloud.refresh_template_repository(enterprise, dc)
    template = find_smallest_template(context, vdc)
    if template:
        vm = cloud.create_virtual_machine(vapp, template)
    return vdc

def cleanup_cloud_compute(config, context):
    """ Cleans up a previously created cloud compute resources. """
    print "### Cleaning up the cloud ###"
    cloud = context.getCloudService()
    for vdc in cloud.listVirtualDatacenters():
        cleanup_cloud_storage(config, context, vdc)
        print "Removing virtual appliances in virtual datacenter %s..." % vdc.getName()
        for vapp in vdc.listVirtualAppliances():
            vapp.delete()
        print "Removing virtual datacenter %s..." % vdc.getName()
        vdc.delete()

