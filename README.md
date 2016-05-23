# python-bulk-email-verifier
Web-based service for Email address verification based on Python+Flask
# UI example
This is how initial upload to the tool looks like
![image](https://cloud.githubusercontent.com/assets/7872919/15464624/4c3c4a0a-20f2-11e6-8af8-fb6bb7150561.png)
And this is progress monitor
![image](https://cloud.githubusercontent.com/assets/7872919/15464626/4f28e9bc-20f2-11e6-8e7d-dd902e3fb317.png)
# Installation
You'll need GIT to download source
```
sudo apt-get update && sudo apt-get install git
```
After that run
```
cd /var/www
git clone https://github.com/danbok/python-bulk-email-verifier/
sudo chown www-data -R python-bulk-email-verifier
```
and 
```
cd python-bulk-email-verifier
sh install.sh
```
vhost content
```
WSGIDaemonProcess verifier user=www-data group=www-data threads=5
WSGIScriptAlias / /var/www/python-bulk-email-verifier/verifier.wsgi

<Directory /var/www/python-bulk-email-verifier/>
    WSGIScriptReloading On
    WSGIProcessGroup verifier
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
</Directory>
```
To start the tool, run
```
nohup celery worker -A verifier_app.tasks --loglevel=INFO --concurrency=12 --purge > celery.out &
```
