# syntax=docker/dockerfile:1
FROM python:3.9
LABEL maintainer="isabharon@gmail.com"
RUN apt-get install -y libmariadb-dev
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
