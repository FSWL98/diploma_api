# Diploma API

REST API server for Diploma project 

## Table of contents

- [Introduction](#introduction)
- [Installing](#installing)
    - [Docker-compose](#with-docker-compose)
    - [Manually](#manually)
- [Usage](#usage)

## Introduction

Server application using flask-restplus and PostgreSQL database for Diploma
Telegram bot.

## Installing

**Clone project**
```bash
$ git clone https://gitlab.com/su.ru.spb/web_dep/anal/api.git --recursive
$ cd anal
```

### Database

This application uses a third party database with PostgreSQL. So, it needs to create and run the database for application working.

If you do not have db dump which you have uploaded to created database, after setting environment variables it can be 
initialized database by the following command:
```bash
flask createdb
```

After committing changes that lead to database model modification use this commands to update your database:
```bash
flask migrate -m "comment describing changes you made"
flask upgrade
```

### Run with docker-compose

- Install [docker-compose](https://docs.docker.com/compose/install/)
- Create docker network by following command:
  ```bash
  docker network create <NETWORK>
  ```
- Set environment variables:
  
  1) Create api.env file inside project root folder with the following variables:
  ```bash
  DB_USER=<DB_USER>
  DB_PASSWD=<DB_PASSWD>
  DB_HOST=<DB_HOST>
  DB_PORT=<DB_PORT> (5432 by default for postgres SQL)
  DB_NAME=<DB_NAME>
  
  SCHEME=<https/http>
  HOST=<HOST> (host of your server. For local running it is `127.0.0.1:5000`)
  FLASK_APP=app_main.py
  
  SECURITY_PASSWORD_SALT=<SECURITY_PASSWORD_SALT> (secret word for encoding the passwords in admin panel - you could use some random string)
  SECRET_KEY=<SECRET_KEY> (secret word for JWT tokens - you could use some random string)
  DEFAULT_USER_NAME=<DEFAULT_USER_NAME> (default admin user first name when initializing the database)
  DEFAULT_USER_SURNAME=<DEFAULT_USER_SURNAME> (default admin last name when initializing the database)
  ADMIN_LOGIN=<ADMIN_USER_NAME> (name for default admin user in flask admin panel - need only for flask createdb command)
  ADMIN_PASSWORD=<ADMIN_USER_PASSWORD> (password for default admin user in flask admin panel - need only for flask createdb command)
  
  REDIS_CELERY_DB_INDEX=<0/1/2> (redis database index for celery tasks storing)
  REDIS_HOST=<REDIS_HOST> (redis instance container name)
  
  MAIL_SERVER=<MAIL_SERVER> (SMTP server host)
  MAIL_PORT=<MAIL_PORT> (SMTP server port)
  MAIL_USERNAME=<MAIL_USERNAME> (SMTP server username)
  MAIL_PASSWORD=<MAIL_PASSWORD> (SMTP server password)
  MAIL_DEFAULT_SENDER=<MAIL_DEFAULT_SENDER> (emails sender)
  
  ELASTICSEARCH_HOST=<ELASTICSEARCH_HOST> (elasticsearch instance container name)
  ELASTICSEARCH_PORT=<ELASTICSEARCH_PORT> (9200 by default)

  PATIENT_NOTIFICATION_URL=<PATIENT_NOTIFICATION_URL> (tg_sdk server url for sending notifications to users)
  STAFF_NOTIFICATION_URL=<STAFF_NOTIFICATION_URL> (tg_sdk server url for sending notifications to staff)
  
  SCHEDULER_HOST=<SCHEDULER_HOST> (sheduler host instance for perfoming such tasks as sending notifications)
  WORKERS=<WORKERS> (number of workers if running server with multiple threads or processes)

  SECRET_KEY_DECODE=<SECRET_KEY_DECODE> (secret word for decoding referral links)
  BOT_START_LINK=<BOT_START_LINK> 
  ```
  2) .env file:
  ```bash
  CONTAINER_API=<CONTAINER_API> (api container name)
  CONTAINER_APSCHEDULER=<CONTAINER_APSCHEDULER> (apscheduler container name)
  CONTAINER_FILEBEAT=<CONTAINER_FILEBEAT> (filebeat container name)
  
  PORT=<PORT> (access port for your app)
  NETWORK=<NETWORK> (external docker network name you created earlier)
  INDEX=<INDEX> (filebeat index for sending logs)
  
  DATA_DIR=<DATA_DIR> (documents storage path)
  DB_VOLUME=<DB_VOLUME> (database storage path)
  DB_HOST=<DB_HOST> (database host the same as in api.env file)
  
  LOG_PATH=<LOG_PATH> (logs storage path)
  
  ELASTICSEARCH_HOST=<ELASTICSEARCH_HOST> (the same as in api.env)  
  ```
  3) db.env file:
  ```bash
  POSTGRES_DB=<POSTGRES_DB> (the same as DB_NAME in api.env)
  POSTGRES_USER=<POSTGRES_USER> (the same as DB_USER in api.env)
  POSTGRES_PASSWORD=<POSTGRES_PASSWORD> (the same as DB_PASSWORD in api.env)
  ```
- Run following commands: 
```bash
$ docker-compose rm -f -s
$ docker-compose build
$ docker-compose up -d
```
You can check setup now by visiting http://127.0.0.1:5000/admin with your browser
(or another address and port depending on your environment HOST and PORT variables)

### Run manually

You have to have python 3.6+ installed to run the application

#### Third party services

You have to run third party services to make it work. The easiest way to launch them is via docker. So first you 
have to [install docker](https://docs.docker.com/get-docker/).

Following steps are to launch these services:

- redis. Example:
```bash
$ sudo docker run --restart unless-stopped -p 6379:6379 --name <redis_container_name> -d redis:3.0.2
```
- elasticsearch. Example:
```bash
$ sudo docker run --restart unless-stopped -p 9200:9200 --name <elasticsearch_container_name> -d elasticsearch:7.10.1
```

#### Setup requirements

Before running the server it needs to setup all packages for server working.

Use the following command for this:
```bash
$ pip3 install -r requirements.txt
```
#### Environment
It needs to export environment variables to start the application manually:
```bash
DB_USER=<DB_USER>

DB_PASSWD=<DB_PASSWD>

DB_HOST=<DB_HOST>

DB_PORT=<DB_PORT>

DB_NAME=<DB_NAME>

SCHEME=<http/https>

HOST=<HOST> (host of your server. For local running it is `127.0.0.1:5000`)

DATA_DIR=<DATA_DIR> (path to multimedia data storage directory)

FLASK_APP=app_main.py

TELEGRAM_TOKEN=<TELEGRAM_TOKEN> (telegram token for sending notifications to bot)

SECURITY_PASSWORD_SALT=<SECURITY_PASSWORD_SALT> (secret word for encoding the passwords in admin panel - you could use some random string)

ADMIN_USER_NAME=<ADMIN_USER_NAME> (name for default admin user in flask admin panel - need only for flask createdb command)

ADMIN_USER_PASSWORD=<ADMIN_USER_PASSWORD> (password for default admin user in flask admin panel - need only for flask createdb command)

REDIS_HOST=<REDIS_HOST> (redis instance host - container name if running via docker-compose)

NOTIFICATION_URL=<NOTIFICATION_URL> (tg_sdk server url for sending notifications to users)

ELASTICSEARCH_HOST=<ELASTICSEARCH_HOST> (elasticsearch instance host - container name if running via docker-compose)

ELASTICSEARCH_PORT=<ELASTICSEARCH_PORT> (elasticsearch instance port - default is 9200)

WORKERS=<WORKERS> (number of workers if running server with multiple threads or processes)

REDIS_CACHE_DB_INDEX=<0/1/2> (redis database index for cache)

REDIS_CELERY_DB_INDEX=1 (redis database index for celery tasks)
```
#### Installing for windows
1) Download Redis. 
https://redis.io/download
Start redis-server.exe
2) Download ElasticSearch.
https://www.elastic.co/downloads/elasticsearch
Start elastic via .\elasticsearch.bat
3) Make sure you have PostgreSQL installed. Download database dump or ask for it.
Check wiki/tools if you aren`t sure how to create db and user in postgres.
 ```bash
 psql -U DB_USER DB_NAME < PATH_TO_DUMP
 ```
4) Clone project 
 ```bash
  git clone https://gitlab.com/su.ru.spb/web_dep/dnpl/api.git --recursive
 ```

 5) Setup .env variables as described in above methods

 6) Install requirements
  ```bash
 pip3 install -r requirements.txt
  ```
 p.s You will not be able to use celery 

#### Celery

The application uses celery supervising background tasks. Specifically, tasks for checking users tasks completing and sending 
notifications. If you want to use these features, you have to run celery.

To start celery worker go to project folder and run following command:
```bash
$ celery -A app_main.celery_app worker -B
```

#### Launch

To start the server you could use:
- _startup.sh_ file
- _uwsgi_, _gunicorn_, etc.
- _flask run_ command

### Usage

The server is started at 127.0.0.1:5000.
- `/admin` - administrator panel (use ADMIN_USER_NAME:ADMIN_USER_PASSWORD for login if you have initialized db with `flask createdb`)
- `/api/v1/swagger` - REST API swagger
