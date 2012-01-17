#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 <address> [<script>]"
    exit 1
fi

# Ensure the classpath file exist
CPFILE=kahuna/abiquo-jars.pth
! [ -f $CPFILE ] && mvn clean compile

# Export the classpath and run the given script
# or open a jython shell if no script arg was given
export CLASSPATH=`cat $CPFILE`
jython -Dabiquo.address=$*
