FROM python:3.6

RUN apt-get update && apt-get install -y wget virtualenv

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs && npm install --global gulp-cli

# Install Chrome (Latest)
RUN apt-get install -y xdg-utils libgtk-3-0 lsb-release libappindicator3-1 fonts-liberation \
  && curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O \
  && dpkg -i google-chrome-stable_current_amd64.deb \
  && rm google-chrome-stable_current_amd64.deb

