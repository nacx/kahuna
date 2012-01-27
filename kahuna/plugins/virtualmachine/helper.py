#!/usr/bin/env jython

from com.abiquo.model.enumerator import HypervisorType
from org.jclouds.abiquo.predicates.cloud import VirtualDatacenterPredicates
from org.jclouds.abiquo.predicates.cloud import VirtualMachineTemplatePredicates

def find_template_by_id(context, id):
    """ Find a template given its id. """
    admin = context.getAdministrationService()
    user = admin.getCurrentUserInfo()
    enterprise = user.getEnterprise()
    return enterprise.findTemplate(VirtualMachineTemplatePredicates.id(id))

def find_compatible_virtual_datacenter(context, template):
    """ Find a virtual datacenter compatible with the given template. """
    template_type = template.getDiskFormatType()
    cloud = context.getCloudService()
    for type in HypervisorType.values():
        if type.isCompatible(template_type):
            vdc = cloud.findVirtualDatacenter(VirtualDatacenterPredicates.type(type))
            if vdc:
                return vdc

