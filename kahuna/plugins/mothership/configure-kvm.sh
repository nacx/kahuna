echo "Umounting mounted nfs repository"
umount /opt/vm_repository
mkdir %(nfsto)s

echo "Configuring new nfs repository"
sed -i /nfs/d /etc/fstab
echo "%(nfsfrom)s %(nfsto)s nfs defaults 0 0" >>/etc/fstab
mount -a

echo "Starting abiquo-aim"
/etc/init.d/abiquo-aim restart
