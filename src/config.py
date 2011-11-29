#!/usr/bin/env jython

from constants import *

from java.util import Properties
from org.jclouds.abiquo import *


config = Properties()
config.put("abiquo.endpoint", ABQ_ENDPOINT)
context = AbiquoContextFactory().createContext(ABQ_USER, ABQ_PASS, config);

