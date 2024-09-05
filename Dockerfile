FROM python:3.10.2
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN apt-get update
RUN pip install -r /requirements.txt
RUN mkdir /app
COPY . /app
WORKDIR /app
