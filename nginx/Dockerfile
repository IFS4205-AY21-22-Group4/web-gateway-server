# syntax=docker/dockerfile:1
FROM nginx:1.20
LABEL maintainer="isabharon@gmail.com"

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
