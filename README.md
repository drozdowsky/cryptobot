Cryptobot
---------
Desc. #todo


How to install:
--------------
* git clone https://github.com/drozdowsky/cryptobot
* cd cryptobot
* mkvirtualenv -a . -r requirements.txt -p python3 cryptobot
* *install* postgresql
* create database 'crypto' (settings.py for more)
* cp crypto/.config.py crypto/config.py   # fill config :)
* python manage.py migrate
* python manage.py runserver 127.0.0.1:420


How to run tasks:
-----------------
* install broker (reddis or rabbitmq) (redis is already configured)
* start celerybeat and celeryworker

alternative ghetto-test way (non asynchronous/dangerous):
* python manage.py shell
* from crypto.tasks `import run_ghetto_way`
* run_ghetto_way()  # will run fetching and executor every one minute


How to test:
------------
* install geckodriver to run e2e tests.
* python manage.py test


TODO:
----
* a lot
