FROM python:3.9.1

COPY fonts/ /usr/share/fonts/truetype/

WORKDIR /usr/src/app

RUN apt-get update && apt-get clean

COPY requirements.txt ./requirements.txt
RUN pip install urllib3
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY templates/ ./templates/

COPY uwsgi.ini ./uwsgi.ini
COPY app_main.py ./app_main.py

COPY startup.sh ./startup.sh
RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

COPY VERSION ./VERSION

RUN mkdir ./data
VOLUME ./data

RUN mkdir ./logs
RUN mkdir ./filebeat_data
RUN chown 1000 ./logs && chgrp 1000 ./logs && chmod 777 ./logs
EXPOSE 5000

CMD sh ./startup.sh
