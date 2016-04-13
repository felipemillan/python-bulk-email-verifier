apt-get update && apt-get upgrade && apt-get install -y python-dev python-pip postfix tor privoxy redis-server expect && pip install -r requirements.txt
mv /etc/privoxy/config /etc/privoxy/config.backup &&
cp ./config /etc/privoxy &&
chmod 777 /etc/privoxy/config &&
chmod 777 database.db &&
service tor restart &&
service privoxy restart &&
sh multi-tor.sh 4 &&
export C_FORCE_ROOT=true