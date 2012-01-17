#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: ${0} <address> [<script>]"
    exit 1
fi

# Export the classpath and run the given script
# or open a jython shell if no script arg was given
export CLASSPATH=`cat kahuna/abiquo-jars.pth`
jython -Dabiquo.address=$*
