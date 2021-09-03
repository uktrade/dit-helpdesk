FROM python:3.6

RUN apt-get update && apt-get install -y wget virtualenv graphviz libgraphviz-dev

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

EXPOSE 8000

RUN mkdir -p /app
WORKDIR /app

VOLUME /reports

ADD . /app/

RUN pip install pipenv
RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt

CMD /app/start.sh
