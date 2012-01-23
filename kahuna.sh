#!/bin/bash

# Exit code to be used when opening an interactive shell
EXIT_OPEN_SHELL=10

# Ensure the classpath file exist
CPFILE=kahuna/abiquo-jars.pth
! [ -f $CPFILE ] && mvn clean compile

# Export the classpath and run the command line script
export CLASSPATH=`cat $CPFILE`
jython kahuna/cli.py $*

# Tricky: If the CLI returns this code, open an interactive shell 
if [ $? -eq $EXIT_OPEN_SHELL ]; then
    jython
fi

