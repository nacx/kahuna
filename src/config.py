#!/usr/bin/env jython

from java.util import Properties
from org.jclouds.abiquo import *

# Abiquo configuration
ABQ_USER = "admin"
ABQ_PASS = "xabiquo"
ABQ_ENDPOINT = "http://10.60.21.33/api"

config = Properties()
config.put("abiquo.endpoint", ABQ_ENDPOINT)
context = AbiquoContextFactory().createContext(ABQ_USER, ABQ_PASS, config);

