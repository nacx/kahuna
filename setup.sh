#!/bin/bash

JYTHON_VERSION=2.5.2
JYTHON_TARGET=/opt/jython-${JYTHON_VERSION}

echo "Downloading Jython ${JYTHON_VERSION}..."
JYTHON_URL=http://sourceforge.net/projects/jython/files/jython/${JYTHON_VERSION}/jython_installer-${JYTHON_VERSION}.jar/download
JYTHON_TMP=/tmp/jython_installer-${JYTHON_VERSION}.jar
wget -q ${JYTHON_URL} -O ${JYTHON_TMP}

echo "Installing Jython ${JYTHON_VERSION} to ${JYTHON_TARGET}..."
java -jar ${JYTHON_TMP} -s -t standard -d ${JYTHON_TARGET}
ln -s ${JYTHON_TARGET}/jython /usr/local/bin/jython
chmow -R a+wx ${JYTHON_TARGET}/cachedir

echo "Addind Easy Install for Jython..."
wget -q http://peak.telecommunity.com/dist/ez_setup.py -O /tmp/ez_setup.py
${JYTHON_TARGET}/jython /tmp/ez_setup.py

echo "Installing Redis egg..."
${JYTHON_TARGET}/bin/easy_install --quiet redis

echo "Installing Kahuna..."
chmod u+x kahuna.sh
ln -s $(pwd)/kahuna.sh /usr/local/bin/kahuna
export JYTHONPATH=$(pwd)

echo "Done!"
echo 
echo "To finish the installation, add the following line to the end of your ~/.bashrc:"
echo "export JYTHONPATH=$(pwd)"
echo
echo "Now you are ready to run 'kahuna'. This will print the available commands and copy"
echo "all default configuration to ~/.kahuna/"
echo "Feel free to edit those files to adapt them to your needs."
echo
echo "Have fun!"

