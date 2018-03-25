nasa_mala_kladionica
====================

Django interni sajt za kladjenje

## Instalacija

* Python 3.x
* MySQL
* memcached
* pip3 install -r requirements.txt

## Deployment

* Clone repo na server
* Napraviti direktorijum /var/log/nmk (www-data)
* Dodati cron za www-data kao `sudo crontab -u www-data -e`:
```
2,17,32,47 * * * * /usr/bin/python /sajtovi/nmk.kokanovic.org/nmkapp/send_shots_cron.py
0 * * * * /usr/bin/python /sajtovi/nmk.kokanovic.org/nmkapp/send_reminder_cron.py
```
* python manage.py collectstatic
