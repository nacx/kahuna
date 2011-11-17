#!/bin/sh

export CLASSPATH=`cat lib/CLASSPATH`

CONTEXT_BUILDER="org.jclouds.abiquo.AbiquoContextBuilder"
PROPS_BUILDER="org.jclouds.abiquo.AbiquoPropertiesBuilder"

ARGS="-Dabiquo.contextbuilder=$CONTEXT_BUILDER -Dabiquo.propertiesbuilder=$PROPS_BUILDER"

jython $ARGS src/infrastructure.py

