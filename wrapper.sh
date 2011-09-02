#!/bin/sh

export CLASSPATH=`cat lib/CLASSPATH`

jython src/infrastructure.py
jython src/storage.py
jython src/cloud.py
jython src/enterprise.py

