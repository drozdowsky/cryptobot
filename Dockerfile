FROM python:3.7-slim

RUN groupadd -r crypto && useradd -r -g crypto crypto

RUN apt-get -y update \
    && apt-get -y install gcc \
    && apt-get clean

# Optimize Dockerfile pip cache
ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# mounting is done in docker-compose.yml
# ADD . /app

# port from uwsgi.ini
EXPOSE 8001

CMD ["uwsgi", "--ini", "/app/cryptobot/uwsgi.ini"]
