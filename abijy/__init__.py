# Set the initial configuration needed to load the classpath
# and the the first time we load the package 'abijy'
import sys

# Set and parse the classpath with the jars we need to call
# jclouds-abiquo methods
f = open(__path__[0] + '/abiquo-jars.pth','r')
abijy_classpath = f.read().split(':')

# Extend the classpath with the jars of the maven repository
sys.path.extend(abijy_classpath)

