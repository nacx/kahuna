# Find which Abiquo profile has been installed
RS=`grep remote-services /etc/abiquo-installer`
ML=`grep monolithic /etc/abiquo-installer`

# Only mount the NFS if it is a Monolithic or a Remote Services installation
if [[ "${RS}" != "" ]] || [[ "${ML}" != "" ]]; then
    NFS=`grep abiquo.appliancemanager.repositoryLocation /opt/abiquo/config/abiquo.properties | awk -F= '{print $2}' | tr -d ' '`
    MOUNT_POINT=`grep abiquo.appliancemanager.localRepositoryPath /opt/abiquo/config/abiquo.properties | awk -F= '{print $2}' | tr -d ' '`

    echo "Umounting mounted nfs repository"
    umount /opt/vm_repository
    mkdir -p ${MOUNT_POINT}

    echo "Configuring new nfs repository"
    sed -i /nfs/d /etc/fstab
    echo "${NFS} ${MOUNT_POINT} nfs defaults 0 0" >>/etc/fstab
    mount -a
fi
