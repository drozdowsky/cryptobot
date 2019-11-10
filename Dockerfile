FROM python:3.7-slim

RUN groupadd -r crypto && useradd -r -g crypto crypto

RUN apt-get -y update \
    && apt-get -y install gcc \
    && apt-get clean

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV SECRET_KEY mysecretkey
ENV PYTHONUNBUFFERED 1
ENV PROCESSES 4
# ./cryptobot/uwsgi.ini port
EXPOSE 8001

RUN python3 manage.py collectstatic --no-input
CMD python3 manage.py migrate && uwsgi --ini /app/cryptobot/uwsgi.ini
