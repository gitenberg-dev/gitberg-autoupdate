FROM python:2

EXPOSE 80

RUN apt-get update && apt-get -y install cron logrotate && apt-get clean

RUN mkdir /var/log/gitenberg
COPY deploy/logrotate-gitberg-autoupdate /etc/logrotate.d/

WORKDIR /usr/src/app

COPY . .
RUN python ./setup.py install

CMD service cron start && exec autoupdate_worker --port 80 --log_file /var/log/gitenberg/autoupdate_worker
