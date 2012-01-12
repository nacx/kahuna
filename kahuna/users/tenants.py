#!/usr/bin/env jython

from kahuna.constants import *
from org.jclouds.abiquo.domain.enterprise import *
from org.jclouds.abiquo.predicates.enterprise import *
from org.jclouds.abiquo.predicates.infrastructure import *


class Tenant:
    """ Provices access to tenant management features.

    This class creates and manages the tenants of the cloud.
    """

    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_enterprise(self, dc, name=ENT_NAME, cpusoft=ENT_CPU_SOFT, cpuhard=ENT_CPU_HARD, ramsoft=ENT_RAM_SOFT, ramhard=ENT_RAM_HARD, ipsoft=ENT_IPS_SOFT, iphard=ENT_IPS_HARD, storagesoft=ENT_STORAGE_SOFT, storagehard=ENT_STORAGE_HARD):
        """ Creates a new enterprise.

        This method will create a new enterprise and assign a datacenter
        to it, so users of that enterprise can start consuming the cloud.
        If the parameters are not specified, the 'ENT_NAME', 'ENT_*_SOFT'
        and 'ENT_*_HARD' limits from the 'constants' module will be used.
        """
        print "Creating enterprise %s..." % name

        # Create the enterprise with the limits
        enterprise = Enterprise.builder(self.__context) \
                     .name(name) \
                     .cpuCountLimits(cpusoft, cpuhard) \
                     .ramLimits(ramsoft, ramhard) \
                     .publicIpsLimits(ipsoft, iphard) \
                     .storageLimits(storagesoft, storagehard) \
                     .build()

        enterprise.save()

        # Allow the enterprise to use a Datacenter
        enterprise.allowDatacenter(dc)

        return enterprise

    def create_user(self, enterprise, name=USR_NAME, surname=USR_SURNAME, role=USR_ROLE, email=USR_EMAIL, nick=USR_LOGIN, password=USR_PASS):
        """ Creates a new user int he given enterprise.

        If the paramters are not specified, the 'USR_NAME', 'USR_SURNAME',
        'USR_ROLE', 'USR_EMAIL', 'USR_LOGIN' and 'USR_PASSWORD' from the 
        'constants' module will be used.
        """
        print "Adding user %s as %s" % (name, role)

        admin = self.__context.getAdministrationService()
        role = admin.findRole(RolePredicates.name(role))

        user = User.builder(self.__context, enterprise, role) \
               .name(name, surname) \
               .email(email) \
               .nick(nick) \
               .password(password) \
               .build()

        user.save()

        return user;

def create_default_tenants(context, dc):
    """ Creates the default tenants.
    
    Creates the default tenants using the 'constants' module properties
    This is just an example of how to use this class.
    """
    print "### Configuring tenants ###"
    ten = Tenant(context)
    enterprise= ten.create_enterprise(dc)
    ten.create_user(enterprise)

def cleanup_default_tenants(context):
    """ Cleans up a previously created default tenants. """
    print "### Cleaning up tenants ###"
    admin = context.getAdministrationService()
    enterprise = admin.findEnterprise(EnterprisePredicates.name(ENT_NAME))
    if enterprise:
        # This will remove the enterprise and all users (if none of them is a Cloud Admin)
        print "Removing enterprise %s and all users..." % enterprise.getName()
        enterprise.delete()

