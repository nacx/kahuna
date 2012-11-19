VERSION="%(version)s"
JENKINS="http://10.60.20.42"

echo "Downloading version ${VERSION}..."
cd /tmp
wget -r -np -nH --reject="index.html*" ${JENKINS}/${VERSION}/

echo "Updating wars..."
rm -rf /opt/abiquo/tomcat/webapps/*

# Find which Abiquo profile has been installed
RS=`grep remote-services /etc/abiquo-installer`
ML=`grep monolithic /etc/abiquo-installer`
V2V=`grep v2v /etc/abiquo-installer`
SRV=`grep server /etc/abiquo-installer`

# Configure according to the installed profiles
if [[ "${RS}" != "" ]] || [[ "${ML}" != "" ]]; then
    mv /tmp/${VERSION}/am.war /opt/abiquo/tomcat/webapps
    mv /tmp/${VERSION}/nodecollector.war /opt/abiquo/tomcat/webapps
    mv /tmp/${VERSION}/ssm.war /opt/abiquo/tomcat/webapps
    mv /tmp/${VERSION}/virtualfactory.war /opt/abiquo/tomcat/webapps
    mv /tmp/${VERSION}/vsm.war /opt/abiquo/tomcat/webapps
fi

if [[ "${V2V}" != "" ]] || [[ "${ML}" != "" ]]; then
    mv /tmp/${VERSION}/bpm-async.war /opt/abiquo/tomcat/webapps/
    rm -f /usr/bin/mechadora
    rm -f /usr/bin/v2v-diskmanager
    cp /tmp/${VERSION}/scripts/* /usr/bin/
fi

if [[ "${SRV}" != "" ]] || [[ "${ML}" != "" ]]; then
    mv /tmp/${VERSION}/api.war /opt/abiquo/tomcat/webapps/
    mv /tmp/${VERSION}/client-premium.war /opt/abiquo/tomcat/webapps/
    mysql -u root kinton </tmp/${VERSION}/database/kinton-schema.sql
fi
