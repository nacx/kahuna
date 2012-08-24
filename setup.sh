#!/bin/bash

function install_jython() {
    echo "Downloading Jython ${JYTHON_VERSION}..."
    JYTHON_URL=http://repo1.maven.org/maven2/org/python/jython-installer/${JYTHON_VERSION}/jython-installer-${JYTHON_VERSION}.jar
    JYTHON_TMP=/tmp/jython_installer-${JYTHON_VERSION}.jar
    wget -q ${JYTHON_URL} -O ${JYTHON_TMP}

    echo "Installing Jython ${JYTHON_VERSION} to ${JYTHON}..."
    mkdir -p ${PREFIX}/lib
    mkdir -p ${PREFIX}/bin
    java -jar ${JYTHON_TMP} -s -t standard -d ${JYTHON}
    ln -s ${JYTHON}/bin/jython ${PREFIX}/bin/jython
}

function install_packages() {
    echo "Adding Easy Install for Jython..."
    wget -q http://peak.telecommunity.com/dist/ez_setup.py -O /tmp/ez_setup.py
    ${JYTHON}/bin/jython /tmp/ez_setup.py

    echo "Installing virtualenv..."
    ${JYTHON}/bin/easy_install --quiet virtualenv
}

function install_kahuna() {
    echo "Creating the Kahuna virtual environment..."
    
    if ! [[ -f ${1}/bin/easy_install ]]; then
        echo "Missing easy_install. Please install it to continue."
        exit 1
    fi
    if ! [[ -f ${1}/bin/virtualenv ]]; then
        echo "Missing virtualenv. Please install it to continue."
        exit 1
    fi

    ${1}/bin/virtualenv ${KAHUNA}

    echo "Installing Redis egg..."
    ${KAHUNA}/bin/easy_install --quiet redis

    echo "Installing Kahuna..."
    chmod -R 777 ${KAHUNA}/cachedir
    chmod u+x kahuna.sh
    [[ -L /usr/local/bin/kahuna ]] && unlink /usr/local/bin/kahuna
    ln -s $(pwd)/kahuna.sh /usr/local/bin/kahuna
}

function print_summary() {
    echo "Done!"
    echo 
    echo "To finish the installation, add the following line to the end of your ~/.bashrc:"
    echo "export KAHUNA_HOME=${KAHUNA}"
    echo
    echo "Now you are ready to run 'kahuna'. This will print the available commands and copy"
    echo "all default configuration to ~/.kahuna/"
    echo "Feel free to edit those files to adapt them to your needs."
    echo
    echo "Have fun!"
}

function usage() {
cat << EOF
Usage: ${0} [-p <install dir>] [-j <jython home>] [-h]
Options:
    -p: Directory where Kahuna will be installed. If the -j option is not set
        Jython will also be installed in this directory.
    -j: If set, Jython will not be installed and Kahuna will use the provided
        Jython installation.
    -h: Prints this help.
EOF
exit 1
}

# Default values
JYTHON_VERSION=2.5.3
PREFIX=/usr/local

while getopts "j:p:h" OPT; do
    case ${OPT} in
        p) PREFIX=${OPTARG} ;;
        j) JYTHON_DIR=${OPTARG} ;;
        h) usage ;;
        ?) usage ;;
    esac
done

JYTHON=${PREFIX}/lib/jython-${JYTHON_VERSION}
KAHUNA=${PREFIX}/lib/kahuna

if [[ -z ${JYTHON_DIR} ]]; then
    install_jython
    install_packages
    JYTHON_DIR=${JYTHON}
fi

install_kahuna ${JYTHON_DIR}
print_summary

