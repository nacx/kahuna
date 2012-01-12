#!/usr/bin/env jython

import sys

from kahuna.cloud.compute import cleanup_cloud_compute
from kahuna.cloud.compute import create_cloud_compute
from kahuna.cloud.storage import cleanup_cloud_storage
from kahuna.cloud.storage import create_cloud_storage
from kahuna.infrastructure.compute import cleanup_infrastructure_compute
from kahuna.infrastructure.compute import create_infrastructure_compute
from kahuna.infrastructure.network import create_infrastructure_network
from kahuna.infrastructure.storage import create_infrastructure_storage
from kahuna.users.tenants import cleanup_default_tenants
from kahuna.users.tenants import create_default_tenants
from kahuna.session import ContextLoader


context = ContextLoader().load_context()

try:
    if len(sys.argv) == 1:
        dc = create_infrastructure_compute(context)
        create_infrastructure_storage(context, dc)
        create_infrastructure_network(context, dc)
        create_default_tenants(context, dc)
        vdc = create_cloud_compute(context, dc)
        create_cloud_storage(context, vdc)
    elif sys.argv[1] == "clean":
        cleanup_cloud_compute(context)
        cleanup_default_tenants(context)
        cleanup_infrastructure_compute(context)
    else:
        print "Usage: %s [clean]" % sys.argv[0]
finally:
    context.close()

