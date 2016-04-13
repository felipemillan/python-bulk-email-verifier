apt-get update && apt-get upgrade && apt-get install -y python-dev python-pip postfix tor privoxy redis-server && pip install -r requirements.txt
mv /etc/privoxy/config /etc/privoxy/config.backup
cp ./config /etc/privoxy
chmod 777 /etc/privoxy/config
service tor restart
service privoxy restart