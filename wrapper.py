import sys
from abicli.session import ContextLoader
from abicli.infrastructure.compute import create_standard_compute
from abicli.infrastructure.storage import create_standard_storage
from abicli.infrastructure.compute import cleanup_infrastructure
from abicli.users.tenants import create_standard_tenants
from abicli.users.tenants import cleanup_tenants
from abicli.cloud.virtualinfrastructure import create_standard_cloud
from abicli.cloud.virtualinfrastructure import cleanup_cloud


context = ContextLoader().load_context()

if len(sys.argv) == 1:
    admin = context.getAdministrationService()
    dc = create_standard_compute(context)
    create_standard_storage(context, dc)
    create_standard_tenants(context, dc)
    create_standard_cloud(context, dc)
elif sys.argv[1] == "clean":
    cleanup_cloud(context)
    cleanup_tenants(context)
    cleanup_infrastructure(context)
else:
    print "Usage: " + sys.argv[0] + " [clean]" 

context.close()
