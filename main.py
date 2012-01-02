#!/usr/bin/env jython

import sys

from abicli.cloud.compute import cleanup_cloud_compute
from abicli.cloud.compute import create_cloud_compute
from abicli.infrastructure.compute import cleanup_infrastructure_compute
from abicli.infrastructure.compute import create_infrastructure_compute
from abicli.infrastructure.network import create_infrastructure_network
from abicli.infrastructure.storage import create_infrastructure_storage
from abicli.users.tenants import cleanup_default_tenants
from abicli.users.tenants import create_default_tenants
from abicli.session import ContextLoader


context = ContextLoader().load_context()

if len(sys.argv) == 1:
    admin = context.getAdministrationService()
    dc = create_infrastructure_compute(context)
    create_infrastructure_storage(context, dc)
    create_infrastructure_network(context, dc)
    create_default_tenants(context, dc)
    create_cloud_compute(context, dc)
elif sys.argv[1] == "clean":
    cleanup_cloud_compute(context)
    cleanup_default_tenants(context)
    cleanup_infrastructure_compute(context)
else:
    print "Usage: " + sys.argv[0] + " [clean]" 

context.close()

