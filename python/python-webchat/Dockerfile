FROM python:slim

COPY . /app

WORKDIR /app

## Libs
RUN apt update && apt install -y \
vim gunicorn curl cron

# COPY cron-nginx /etc/cron.d/cron-nginx
# COPY nginx/* /etc/nginx/sites-available/default

# RUN /etc/init.d/cron start

# RUN /bin/bash -c crontab /etc/cron.d/cron-nginx

# Requirements
RUN pip install -r requirements.txt
# ENTRYPOINT [ "python", "main.py" ]
