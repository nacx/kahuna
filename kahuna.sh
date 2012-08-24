#!/bin/sh

[ -z "$KAHUNA_HOME" ] && export KAHUNA_HOME="/usr/local/lib/kahuna"

# Exit code to be used when opening an interactive shell
EXIT_OPEN_SHELL=10

# Allow creating symlinks in the path to point to this
# script
if [ -h $0 ]; then
    BASEDIR=`readlink $0 | xargs dirname`
else
    BASEDIR=`dirname $0`
fi

# Enter the real directori before performing any operation
cd $BASEDIR
export JYTHONPATH=$BASEDIR

# Ensure the classpath file exist
CPFILE=kahuna/abiquo-jars.pth
! [ -f $CPFILE ] && mvn clean compile -U

# Export the classpath and run the command line script
export CLASSPATH=`cat $CPFILE`
${KAHUNA_HOME}/bin/jython kahuna/cli.py $*

# Tricky: If the CLI returns this code, open an interactive shell 
if [ $? -eq $EXIT_OPEN_SHELL ]; then
    ${KAHUNA_HOME}/bin/jython
fi

