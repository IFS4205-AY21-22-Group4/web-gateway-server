# syntax=docker/dockerfile:1
FROM python:3.9
LABEL maintainer="isabharon@gmail.com"

# Create user and group
ENV SERVICE=/home/app/web-gateway
RUN addgroup --system web-gateway && adduser --system web-gateway --group

# Create app directories
RUN mkdir -p $SERVICE
RUN mkdir -p $SERVICE/static

# Set work directory
WORKDIR $SERVICE

# Install necessary packages
RUN apt-get install -y libmariadb-dev

# Set python environment variables
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install --upgrade pip
COPY . $SERVICE
RUN pip install -r requirements.txt
