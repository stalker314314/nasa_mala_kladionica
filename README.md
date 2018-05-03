nasa_mala_kladionica
====================

[![Build Status](https://travis-ci.org/stalker314314/nasa_mala_kladionica.svg?branch=master)](https://travis-ci.org/stalker314314/nasa_mala_kladionica)
[![Coverage Status](https://coveralls.io/repos/github/stalker314314/nasa_mala_kladionica/badge.svg)](https://coveralls.io/github/stalker314314/nasa_mala_kladionica)

Django interni sajt za kladjenje

## Instalacija

Ne pratiti slepo:)

```
sudo apt-get update
sudo apt-get -y install gettext python3-pip memcached apache2 libapache2-mod-wsgi-py3 postgresql postgresql-client-9.6

sudo -u postgres psql
  create user sharkzbet with password '<your_DB_password>';
  create database "sharkzbet";
  grant all privileges on database 'sharkzbet' to sharkzbet;

sudo mkdir /var/log/sharkz.bet
sudo chown www-data:www-data /var/log/sharkz.bet

sudo mkdir /sites
sudo chown $USER:$USER /sites
ssh-keygen -t rsa -b 4096 -C "branko@kokanovic.org" -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub
# Put that to github

git clone git@github.com:stalker314314/nasa_mala_kladionica.git /sites/sharkz.bet
chmod 777 /sites/sharkz.bet/ -R
cd /sites/sharkz.bet/
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
  export NMK_DB_USER=sharkzbet
  export NMK_DB_PASSWORD=<your_DB_password>
  export NMK_MAILJET_API_KEY='1<mailjet_api_key>'
  export NMK_MAILJET_SECRET_KEY='<mailjet_secret_key>'

sudo cp /sites/sharkz.bet/sharkz.bet.conf /etc/apache2/sites-available
sudo a2ensite sharkz.bet.conf
sudo service apache2 restart

# Setting cert
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-apache
sudo certbot --apache
sudo certbot renew --dry-run
sudo crontab -e
  10 0 * * * certbot renew

# cron jobs
cat <<EOF > /home/kokan/send_shots_cron.sh
#!/bin/bash
source /etc/apache2/envvars
/usr/bin/python3 /sites/sharkz.bet/nmkapp/send_shots_cron.py
EOF
chmod a+x /home/kokan/send_shots_cron.sh

cat <<EOF > /home/kokan/send_reminder_cron.sh
#!/bin/bash
source /etc/apache2/envvars
/usr/bin/python3 /sites/sharkz.bet/nmkapp/send_reminder_cron.py
EOF
chmod a+x /home/kokan/send_reminder_cron.sh

sudo crontab -u www-data -e
  2,17,32,47 * * * * /home/kokan/send_shots_cron.sh
  0 * * * * /home/kokan/send_reminder_cron.sh
```