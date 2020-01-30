FROM python:3.6

RUN apt-get update && apt-get install -y wget virtualenv


ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs && npm install --global gulp-cli

EXPOSE 8000

RUN mkdir -p /app
WORKDIR /app

VOLUME /reports

ADD requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/development.txt

ADD . /app/

CMD /app/compose/automation/django/start.sh
