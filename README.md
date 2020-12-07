Cryptobot
=========
Web app to manage crypto market with rules.


How to install:
--------------
* docker-compose up
* docker-compose exec web python manage.py collectstatic --noinput
* docker-compose exec web python manage.py migrate
* http://127.0.0.1/ (app runs on default http port :80)
