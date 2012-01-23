#!/bin/bash

# Ensure the classpath file exist
CPFILE=kahuna/abiquo-jars.pth
! [ -f $CPFILE ] && mvn clean compile

# Export the classpath and run the command line script
export CLASSPATH=`cat $CPFILE`
jython kahuna/cli.py $*
