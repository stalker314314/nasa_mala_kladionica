nasa_mala_kladionica
====================

Django interni sajt za kladjenje

## Instalacija

* Python 2.7 (moze i 3.x)
* Django 1.7
* MySQL
* memcached
* pip install djrill
* pip install python-memcached
* https://github.com/django-debug-toolbar/django-debug-toolbar
* pip install mysql-python

## Deployment

* Clone repo na server
* Napraviti direktorijum /var/log/nmk (www-data)
* Dodati cron za www-data kao `sudo crontab -u www-data -e`:
```
2,17,32,47 * * * * /usr/bin/python /sajtovi/nmk.kokanovic.org/nmkapp/send_shots_cron.py
0 * * * * /usr/bin/python /sajtovi/nmk.kokanovic.org/nmkapp/send_reminder_cron.py
```
* python manage.py collectstatic
