echo "mount nfs repository"
umount /opt/vm_repository
mount 10.60.1.104:/volume1/nfs-devel /opt/vm_repository

echo "start abiquo-aim"
/etc/init.d/abiquo-aim restart
