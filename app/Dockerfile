FROM python:3.9
MAINTAINER Semyon Tikhomirov <kpowjemegaman@gmail.com>
RUN apt-get update
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
ADD main.py /app
ADD main.py /
ADD config.py /app
RUN pip install -r requirements.txt
ENV FLASK_ENV="docker"
EXPOSE 5000