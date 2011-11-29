#!/bin/sh

export CLASSPATH=`cat lib/CLASSPATH`

CONTEXT_BUILDER="org.jclouds.abiquo.AbiquoContextBuilder"
PROPS_BUILDER="org.jclouds.abiquo.AbiquoPropertiesBuilder"

ARGS="-Dabiquo.contextbuilder=$CONTEXT_BUILDER -Dabiquo.propertiesbuilder=$PROPS_BUILDER"

if [ $# -eq 0 ]; then
    jython $ARGS src/infrastructure.py
    jython $ARGS src/tenants.py
    jython $ARGS src/storage.py
elif [ "$1" = "clean" ]; then
    jython $ARGS src/cleanup.py
else
    echo "Usage: $0 [clean]"
    exit 1
fi

