FROM python:3.6

RUN apt-get update && apt-get install -y wget virtualenv

RUN apt-get install -y python3-venv

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs && npm install --global gulp-cli

# Install Chrome (Latest)
RUN apt-get install -y xvfb xdg-utils libgtk-3-0 lsb-release libappindicator3-1 fonts-liberation libasound2 libnspr4 libnss3 \
  && curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O \
  && dpkg -i google-chrome-stable_current_amd64.deb \
  && rm google-chrome-stable_current_amd64.deb

# Install dependency to unzip chromedriver
RUN apt-get install -y zip unzip

# Install chromedriver
RUN cd $HOME/Downloads \
  && wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip \
  && mkdir -p $HOME/bin \
  && mv chromedriver $HOME/bin \
  && export PATH=$PATH:$HOME/bin
