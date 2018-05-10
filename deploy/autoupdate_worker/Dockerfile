FROM python:2

EXPOSE 80

RUN apt-get update && apt-get -y install cron logrotate ruby xsltproc xvfb calibre git libjpeg-dev libpng-dev libfreetype6-dev zlib1g-dev libxml2-dev libxslt1-dev tidy && apt-get clean
RUN gem install tilt
RUN pip install git+https://github.com/gitenberg-dev/pg-epubmaker git+https://github.com/gitenberg-dev/gitberg-build
RUN gem install asciidoctor -v 1.5.2

RUN git clone https://github.com/gitenberg-dev/asciidoctor-htmlbook.git && pip install -r asciidoctor-htmlbook/gitberg-machine/requirements.txt && rm -r asciidoctor-htmlbook

RUN mkdir /var/log/gitenberg
COPY deploy/logrotate-gitberg-autoupdate /etc/logrotate.d/

WORKDIR /usr/src/app

# This is slow, so avoid having to do it every time.
RUN pip install boto3 travispy
COPY . .
RUN pip install . --process-dependency-links

CMD service cron start && exec autoupdate_worker --port 80 --log_file /var/log/gitenberg/autoupdate_worker
