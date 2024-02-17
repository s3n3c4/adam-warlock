FROM python:slim

COPY . /app

WORKDIR /app

## Libs
RUN apt update && apt install -y \
vim curl

# Requirements
RUN pip install -r requirements.txt

