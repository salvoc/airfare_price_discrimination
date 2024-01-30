# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice
# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR /apd

# Install essential packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome (root image is debian)
# See https://stackoverflow.com/questions/49132615/installing-chrome-in-docker-file
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000
