#!/usr/bin/env jython

from com.abiquo.model.enumerator import *
from java.lang import System


## Abiquo ##

# Abiquo configuration
ABQ_ADDRESS = "10.60.1.222"
ABQ_USER = "admin"
ABQ_PASS = "xabiquo"
ABQ_ENDPOINT = "http://" + ABQ_ADDRESS + "/api"


## Infrastructure ##

# Datacenter configuration
DC_NAME = "Hawaii"              # The name of the datacenter
DC_LOCATION = "Honolulu"        # The location of the datacenter
DC_ADDRESS = ABQ_ADDRESS        # The address of the remote services

# Rack configuration
RACK_NAME = "Coconut rack"
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
TIER_NAME = "Seaside Storage"           # The name of the tier where the pool will be added

# Device configuration
DEV_NAME = "Kai"                        # The name of the device
DEV_TYPE = StorageTechnologyType.LVM    # The device type
DEV_ADDRESS = "10.60.21.177"            # The device address

# Pool configuration
POOL_NAME = "abiquo"                    # The storage pool to use in the storage device

# Volume configuration
VOL_NAME = "Cocovol"                    # The name of the volume
VOL_SIZE = 16                           # Size of the volume in MB


## Networking ##

# Public network configuration
PN_NAME = "Coconet"                     # The name of the public network
PN_TAG =  5                             # Public network tag
PN_ADDRESS = "80.12.96.0"               # The network address of the network
PN_MASK = 25                            # The mask of the network
PN_GATEWAY = "80.12.96.1"               # The default gateway for the network
PN_DNS = "8.8.8.8"                      # Primary DNS

# External network configuration
EXT_NAME = "Kainet"                      # The name of the external network
EXT_TAG =  6                             # External network tag
EXT_ADDRESS = "10.60.30.0"               # The network address of the network
EXT_MASK = 25                            # The mask of the network
EXT_GATEWAY = "10.60.30.1"             # The default gateway for the network
EXT_DNS = "8.8.8.8"                      # Primary DNS


## Cloud ##

# Virtual datacenter configuration
VDC_NAME = "Kaahumanu"                  # The name of the virtual datacenter
VDC_ENTERPRISE = "Abiquo"               # The enterprise where the virtual datacenter will be created

# Private network configuration
NET_NAME = "Kaahumanu Network"          # The name of the private network for the virtual datacenter
NET_ADDRESS = "192.168.1.0"             # The network address of the network
NET_MASK = 24                           # The mask of the network
NET_GATEWAY = "192.168.1.1"             # The default gateway for the network

# Virtual appliance configuration
VAPP_NAME = "Kalakaua"                  # The name of the virtual appliance


## Enterprise ##

# Enterprise configuration
ENT_NAME = "Surfing Cloud"                  # Enterprise name
ENT_CPU_SOFT = 5                            # Soft limut for the number of CPU
ENT_CPU_HARD = 10                           # Maximum CPU available
ENT_RAM_SOFT = 2048                         # Soft limit for the available RAM in MB
ENT_RAM_HARD = 4096                         # Maximum available RAM in MB
ENT_IPS_SOFT = 5                            # Soft limit for the number of public IPs
ENT_IPS_HARD = 10                           # Maximum number of available public IPs
ENT_STORAGE_SOFT = 5120 * 1024 * 1024       # Soft limit for external storage in bytes
ENT_STORAGE_HARD = 10240 * 1024 * 1024      # Maximum available external storage in bytes

# User configuration
USR_ROLE = "ENTERPRISE_ADMIN"               # The role for the user
USR_NAME = "Aloha"                          # Name of the user
USR_SURNAME = "Administrator"               # Surname of the user
USR_EMAIL = "eadmin@surfingcloud.com"       # Surname of the user
USR_LOGIN = "aloha"                         # The login name
USR_PASS = "aloha"                          # The password

