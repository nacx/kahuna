echo "mount nfs repository"
umount /opt/vm_repository
mount '%(nfsfrom)s' '%(nfsto)s'

echo "start abiquo-aim"
/etc/init.d/abiquo-aim restart
