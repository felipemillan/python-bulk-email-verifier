# python-bulk-email-verifier
Web-based service for Email address verification based on Python+Flask
# UI example
This is how initial upload to the tool looks like
![image](https://cloud.githubusercontent.com/assets/7872919/14596854/f31282ac-056a-11e6-8fd7-14c4e092e517.png)
And this is progress monitor
![image](https://cloud.githubusercontent.com/assets/7872919/14596855/f3143926-056a-11e6-8685-29f48ec492df.png)
# Installation
You'll need GIT to download source
```
sudo apt-get update && sudo apt-get install git
```
After that run
```
git clone https://github.com/danbok/python-bulk-email-verifier/
```
and 
```
cd python-bulk-email-verifier
sh install.sh
```
To start the tool, run
```
nohup python manage.py server > manage.out &
```
And visit your IP's 8080 port.
