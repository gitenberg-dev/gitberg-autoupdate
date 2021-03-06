FROM python:3

EXPOSE 80

RUN apt-get update && apt-get -y install cron logrotate ruby xsltproc xvfb calibre git libjpeg-dev libpng-dev libfreetype6-dev zlib1g-dev libxml2-dev libxslt1-dev tidy && apt-get clean
RUN gem install tilt
RUN pip install 'ebookmaker==0.8.7'
RUN gem install asciidoctor -v 1.5.2

RUN git clone https://github.com/gitenberg-dev/asciidoctor-htmlbook.git && pip install -r asciidoctor-htmlbook/gitberg-machine/requirements.txt && rm -r asciidoctor-htmlbook

RUN mkdir /var/log/gitenberg
COPY deploy/logrotate-gitberg-autoupdate /etc/logrotate.d/

WORKDIR /usr/src/app

# This is slow, so avoid having to do it every time.
RUN pip install boto3 github3.py requests GitPython rdflib-jsonld
COPY deploy/config.yaml /root/.config/gitberg/config.yaml
COPY deploy/known_hosts /root/.ssh/known_hosts
COPY deploy/id_rsa_password /root/.ssh/id_rsa
RUN chmod 0600 /root/.ssh/id_rsa
COPY deploy/.gitconfig /root/.gitconfig
COPY . .
RUN pip install . 

CMD service cron start && ssh-keygen -p -P $SSH_KEY_PASSWORD -N "" -f /root/.ssh/id_rsa && exec autoupdate_worker --port 80 --log_file /var/log/gitenberg/autoupdate_worker
