nasa_mala_kladionica
====================

[![Build Status](https://travis-ci.org/stalker314314/nasa_mala_kladionica.svg?branch=master)](https://travis-ci.org/stalker314314/nasa_mala_kladionica)
[![Coverage Status](https://coveralls.io/repos/github/stalker314314/nasa_mala_kladionica/badge.svg)](https://coveralls.io/github/stalker314314/nasa_mala_kladionica)

Django interni sajt za kladjenje

## Instalacija

Ne pratiti slepo:)

```
sudo apt-get update
sudo apt-get -y install git gettext python3-pip memcached apache2 libapache2-mod-wsgi-py3 postgresql postgresql-client

sudo -u postgres psql
  create user nmkbet with password '<your_DB_password>';
  create database nmkbet;
  grant all privileges on database nmkbet to nmkbet;

sudo mkdir /var/log/nmk.bet
sudo chown www-data:www-data /var/log/nmk.bet

sudo mkdir /sites
sudo chown $USER:$USER /sites
ssh-keygen -t rsa -b 4096 -C "branko@kokanovic.org" -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub
# Put that to github

git clone git@github.com:stalker314314/nasa_mala_kladionica.git /sites/nmk.bet
chmod 777 /sites/nmk.bet/ -R
cd /sites/nmk.bet/
git config core.filemode false
sudo pip3 install -Ur requirements.txt
python3 manage.py collectstatic
python3 manage.py compilemessages
python3 manage.py migrate
python3 manage.py createsuperuser

sudo vim /etc/apache2/envvars
  export NMK_DEBUG=0
  export NMK_SECRET_KEY='<your_secret_key>'
  export NMK_DB_HOST=127.0.0.1
  export NMK_DB_NAME=nmkbet
  export NMK_DB_USER=nmkbet
  export NMK_DB_PASSWORD=<your_DB_password>
  export NMK_MAILJET_API_KEY='<mailjet_api_key>'
  export NMK_MAILJET_SECRET_KEY='<mailjet_secret_key>'
  export NMK_GOOGLE_OAUTH2_KEY='<google_oauth_key>'
  export NMK_GOOGLE_OAUTH2_SECRET='<google_oauth_secret>'

sudo cp /sites/nmk.bet/nmk.bet.conf /etc/apache2/sites-available
sudo a2ensite nmk.bet.conf
sudo service apache2 restart

# Setting cert
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python3-certbot-apache
sudo certbot --apache
sudo certbot renew --dry-run
sudo crontab -e
  10 0 * * * certbot renew

# cron jobs
cat <<EOF > /home/kokan/send_shots_cron.sh
#!/bin/bash
source /etc/apache2/envvars
/usr/bin/python3 /sites/nmk.bet/nmkapp/send_shots_cron.py
EOF
chmod a+x /home/kokan/send_shots_cron.sh

cat <<EOF > /home/kokan/send_reminder_cron.sh
#!/bin/bash
source /etc/apache2/envvars
/usr/bin/python3 /sites/nmk.bet/nmkapp/send_reminder_cron.py
EOF
chmod a+x /home/kokan/send_reminder_cron.sh

sudo crontab -u www-data -e
  2,17,32,47 * * * * /home/kokan/send_shots_cron.sh
  0 * * * * /home/kokan/send_reminder_cron.sh
```