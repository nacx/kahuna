#!/usr/bin/env jython

from config import *

from org.jclouds.abiquo.domain.enterprise import *
from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *


def create_enterprise(context):
    print "Creating enterprise %s..." % ENT_NAME

    # Create the enterprise with the limits
    enterprise = Enterprise.builder(context) \
                 .name(ENT_NAME) \
                 .cpuCountLimits(ENT_CPU_SOFT, ENT_CPU_HARD) \
                 .ramLimits(ENT_RAM_SOFT, ENT_RAM_HARD) \
                 .publicIpsLimits(ENT_IPS_SOFT, ENT_IPS_HARD) \
                 .storageLimits(ENT_STORAGE_SOFT, ENT_STORAGE_HARD) \
                 .build()

    enterprise.save()

    # Allow the enterprise to use a Datacenter
    admin = context.getAdministrationService()
    datacenter = admin.findDatacenter(DatacenterPredicates.datacenterName(DC_NAME))
    enterprise.allowDatacenter(datacenter)

    return enterprise

def create_user(enterprise):
    print "Adding user %s as %s" % (USR_NAME, USR_ROLE)

    admin = context.getAdministrationService()
    role = admin.findRole(RolePredicates.roleName(USR_ROLE))

    user = User.builder(context, enterprise, role) \
           .name(USR_NAME, USR_SURNAME) \
           .email(USR_EMAIL) \
           .nick(USR_LOGIN) \
           .password(USR_PASS) \
           .build()

    user.save()

    return user;


if __name__ == '__main__':

    # Context variable is initialised in config.py

    enterprise = create_enterprise(context)
    user = create_user(enterprise)

    # Close the connection to the Abiquo API
    context.close()

