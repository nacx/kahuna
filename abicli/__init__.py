# Set the initial configuration needed to load the classpath
# and the system properties the first time we load the package
# 'abicli'
import sys

# set and parse the classpath of the jars we use for call the 
# jclouds-client
f = open(__path__[0] + '/abiquo-jars.pth','r')
abijy_classpath = f.read().split(':')

# extend the classpath with the jars of the maven repository
sys.path.extend(abijy_classpath)

# Now we can load Java classes. Set the context builder
# in session.
from java.lang import System
context_builder="org.jclouds.abiquo.AbiquoContextBuilder"
props_builder="org.jclouds.abiquo.AbiquoPropertiesBuilder"
System.setProperty("abiquo.contextbuilder", context_builder)
System.setProperty("abiquo.propertiesbuilder", props_builder)

