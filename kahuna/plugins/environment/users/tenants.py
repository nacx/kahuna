#!/usr/bin/env jython

from com.google.common.base import Predicates
from org.jclouds.abiquo.domain.enterprise import Enterprise
from org.jclouds.abiquo.domain.enterprise import User
from org.jclouds.abiquo.predicates.enterprise import EnterprisePredicates
from org.jclouds.abiquo.predicates.enterprise import RolePredicates

class Tenant:
    """ Provices access to tenant management features. """

    def __init__(self, context):
        """ Initialize with an existent context. """
        self.__context = context

    def create_enterprise(self, dc, name, cpusoft, cpuhard, ramsoft, ramhard,
            ipsoft, iphard, storagesoft, storagehard):
        """ Creates a new enterprise. """
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

    def create_user(self, enterprise, name, surname, role, email, nick, password):
        """ Creates a new user int he given enterprise. """
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

def create_default_tenants(config, context, dc):
    """ Creates the default tenants using the plugin config values. """
    print "### Configuring tenants ###"
    ten = Tenant(context)
    enterprise= ten.create_enterprise(dc, config.get("enterprise", "name"),
            config.getint("enterprise", "cpu-soft"),
            config.getint("enterprise", "cpu-hard"),
            config.getint("enterprise", "ram-soft"),
            config.getint("enterprise", "ram-hard"),
            config.getint("enterprise", "public-ips-soft"),
            config.getint("enterprise", "public-ips-hard"),
            config.getint("enterprise", "storage-soft"),
            config.getint("enterprise", "storage-hard"))
    ten.create_user(enterprise, config.get("user", "name"),
            config.get("user", "surname"),
            config.get("user", "role"),
            config.get("user", "email"),
            config.get("user", "login"),
            config.get("user", "password"))

def cleanup_default_tenants(config, context):
    """ Cleans up a previously created default tenants. """
    print "### Cleaning up tenants ###"
    admin = context.getAdministrationService()
    enterprises = admin.listEnterprises(Predicates.not(EnterprisePredicates.name("Abiquo")))
    for enterprise in enterprises:
        # This will remove the enterprise and all users (if none of them is a Cloud Admin)
        print "Removing enterprise %s and all users..." % enterprise.getName()
        enterprise.delete()

