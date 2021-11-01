# syntax=docker/dockerfile:1
FROM python:3.9
LABEL maintainer="isabharon@gmail.com"

# Create user and group
ENV SERVICE=/home/app/web-gateway
RUN useradd -m web-gateway

# Create app directories
RUN mkdir -p $SERVICE

# Set work directory
WORKDIR $SERVICE

# Set python environment variables
ENV PYTHONUNBUFFERED=1

# Install necessary packages
RUN apt-get install -y libmariadb-dev

COPY . $SERVICE
RUN chown -R web-gateway:web-gateway $SERVICE

# Run as unprivileged
USER web-gateway
ENV PATH="/home/web-gateway/.local/bin:${PATH}"

# Install dependencies
RUN pip install --upgrade pip --user
RUN pip install -r requirements.txt --user
