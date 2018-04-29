nasa_mala_kladionica
====================

[![Build Status](https://travis-ci.org/stalker314314/nasa_mala_kladionica.svg?branch=master)](https://travis-ci.org/stalker314314/nasa_mala_kladionica)
[![Coverage Status](https://coveralls.io/repos/github/stalker314314/nasa_mala_kladionica/badge.svg)](https://coveralls.io/github/stalker314314/nasa_mala_kladionica)

Django interni sajt za kladjenje

## Instalacija

* Python 3.x
* PostgreSQL
* memcached (opciono)
* pip3 install -r requirements.txt

## Deployment

* Clone repo na server
* Napraviti direktorijum /var/log/nmk (www-data)
* Dodati cron za www-data kao `sudo crontab -u www-data -e`:
```
2,17,32,47 * * * * /usr/bin/python /sites/nmk.kokanovic.org/nmkapp/send_shots_cron.py
0 * * * * /usr/bin/python /sites/nmk.kokanovic.org/nmkapp/send_reminder_cron.py
```
* python manage.py collectstatic
* python manage.py compilemessages
