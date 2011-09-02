#!/usr/bin/env jython

from com.abiquo.model.enumerator import *

from com.apiclient.wrapper.admin import *
from com.apiclient.connection import *


# Storage device configuration
ST_NAME = "Nexenta"
ST_TYPE = StorageTechnologyType.NEXENTA
ST_MANAGEMENT_IP = "10.60.20.23"
ST_MANAGEMENT_PORT = 8080
ST_ISCSI_IP = "10.60.20.23"
ST_ISCSI_PORT = 3260

# Storage pool configuration
SP_NAME = "abiquo"
SP_TIER = "Default Tier 1"


def create_device(datacenter):
    device = StorageDevice(datacenter, ST_NAME, ST_MANAGEMENT_IP,
            ST_MANAGEMENT_PORT, ST_ISCSI_IP, ST_ISCSI_PORT, ST_TYPE)
    device.save()
    return device

def create_pool(device):
    pools = device.getRemoteStoragePools()
    tiers = device.getDatacenter().getTiers()
    pool = filter(lambda p: p.getName() == SP_NAME, pools)[0]
    tier = filter(lambda t: t.getName() == SP_TIER, tiers)[0]

    pool.setTier(tier)
    pool.save()

    return pool
    

if __name__ == '__main__':
    datacenter = ApiConnection.getConnection().getDatacenters()[0]

    device = create_device(datacenter)
    pool = create_pool(device)

