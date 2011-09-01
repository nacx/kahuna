#!/usr/bin/env jython

from com.apiclient.wrapper.admin import *
from com.apiclient.connection.constants import *

# Datacenter configuration
DC_NAME = "Jython"
DC_LOCATION = "Honolulu"
DC_ADDRESS = "10.60.1.222"


def create_datacenter():
    dc = Datacenter(DC_NAME, DC_LOCATION, DC_ADDRESS, AbiquoKeyWords.AbiquoEdition.ENTERPRISE)
    dc.save()


if __name__ == '__main__':
    create_datacenter();

