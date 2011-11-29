#!/usr/bin/env jython

from com.abiquo.model.enumerator import *

## Abiquo ##

# Abiquo configuration
ABQ_ADDRESS = "10.60.1.222"
ABQ_USER = "admin"
ABQ_PASS = "xabiquo"
ABQ_ENDPOINT = "http://" + ABQ_ADDRESS + "/api"


## Infrastructure ##

# Datacenter configuration
DC_NAME = "Datacenter"          # The name of the datacenter
DC_LOCATION = "Honolulu"        # The location of the datacenter
DC_ADDRESS = ABQ_ADDRESS        # The address of the remote services

# Rack configuration
RACK_NAME = "API rack"
RACK_VLAN_MIN = 3       # Minimum VLAN tag
RACK_VLAN_MAX = 500     # Maximum VLAN tag
RACK_NRSQ = 10          # VLAN pool size for VDC that exceed reservation

# Machine configuration
PM_ADDRESS = "10.60.1.79"               # Hypervisor address
PM_TYPE = HypervisorType.XENSERVER      # Hypervisor type
PM_USER = "root"                        # Hypervisor login
PM_PASSWORD = "temporal"                # Hypervisor password
PM_VSWITCH = "eth1"                     # Virtual switch where VLANs will be attached
PM_DATASTORE = "Local storage"          # Datastore where VM disks will be deployed


## Storage ##

# Tier configuration
TIER_NAME = "LVM Storage"

# Device configuration
DEV_NAME = "LVM Mothership"
DEV_TYPE = StorageTechnologyType.LVM
DEV_ADDRESS = "10.60.21.177"

# Pool configuration
POOL_NAME = "abiquo"


## Enterprise ##

# Enterprise configuration
ENT_NAME = "API Enterprise"     # Enterprise name
ENT_CPU_SOFT = 5                # Soft limut for the number of CPU
ENT_CPU_HARD = 10               # Maximum CPU available
ENT_RAM_SOFT = 2048             # Soft limit for the available RAM in MB
ENT_RAM_HARD = 4096             # Maximum available RAM in MB
ENT_IPS_SOFT = 5                # Soft limit for the number of public IPs
ENT_IPS_HARD = 10               # Maximum number of available public IPs
ENT_STORAGE_SOFT = 5120 * 1024 * 1024         # Soft limit for external storage in bytes
ENT_STORAGE_HARD = 10240 * 1024 * 1024        # Maximum available external storage in bytes

# User configuration
USR_ROLE = "ENTERPRISE_ADMIN"           # The role for the user
USR_NAME = "Ignasi"                     # Name of the user
USR_SURNAME = "Barrera"                 # Surname of the user
USR_EMAIL = "ent-admin@abiquo.com"      # Surname of the user
USR_LOGIN = "ibarrera"                  # The login name
USR_PASS = "ibarrera"                   # The password

