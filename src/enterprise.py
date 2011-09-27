#!/usr/bin/env jython

from java.util import Locale

from com.apiclient.wrapper.infrastructure import *
from com.apiclient.wrapper.enterprise import *
from com.apiclient.connection import *
from com.apiclient.connection.constants import *


# Enterprise configuration
ENT_NAME = "Abijy"

# User configuration
USR_NAME = "Ignasi"
USR_SURNAME = "Barrera"
USR_EMAIL = "ignasi.barrera@abiquo.com"
USR_LOGIN = "nacx"
USR_PASSWORD = "ef6299c9e7fdae6d775819ce1e2620b8" # md5(temporal)
USR_ROLE = "ENTERPRISE_ADMIN"


def create_enterprise():
    enterprise = Enterprise(ENT_NAME)
    enterprise.save()

    # Add a datacenter to the enterprise, if any
    datacenters = Admin.getDatacenters()
    if datacenters:
	enterprise.allowDatacenter(datacenters[0])

    return enterprise

def create_user(enterprise):
    roles = Admin.getGlobalRoles()
    role = filter(lambda r: r.getName() == USR_ROLE, roles)[0]

    user = User(enterprise, role, USR_NAME, USR_SURNAME, USR_LOGIN, "", 
            USR_EMAIL, Locale.ENGLISH, USR_PASSWORD, True, AbiquoKeyWords.AuthType.ABIQUO)

    user.save()

    return user


if __name__ == '__main__':
    enterprise = create_enterprise();
    create_user(enterprise)

