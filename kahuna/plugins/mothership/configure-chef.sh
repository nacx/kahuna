# The COOKBOOKS variable is defined in the mothership.py plugin

COOKBOOK_DIR=${HOME}/cookbooks

echo "Installing git..."
apt-get install -y git-core

for CBK in ${COOKBOOKS[*]}; do
    echo "Downloading cookbook: ${CBK}"
    DIR=${COOKBOOK_DIR}/${CBK}
    mkdir -p ${DIR}
    git clone https://github.com/cookbooks/${CBK} ${DIR}
done

echo "Adding permissions to read the keys..."
chmod a+r /etc/chef/*.pem

echo "Uploading cookbooks..."
knife cookbook upload -a -VV -o ${COOKBOOK_DIR} -s http://localhost:4000 -u chef-webui -k /etc/chef/webui.pem

