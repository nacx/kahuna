# Set the initial configuration needed to load the classpath
# and the the first time we load the package 'kahuna'
from __future__ import with_statement
import sys

# Set and parse the classpath with the jars we need to call
# jclouds-abiquo methods
with open(__path__[0] + '/abiquo-jars.pth','r') as f:
    kahuna_classpath = f.read().split(':')
    # Extend the classpath with the jars of the maven repository
    sys.path.extend(kahuna_classpath)

