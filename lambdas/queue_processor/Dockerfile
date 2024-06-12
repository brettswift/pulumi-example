FROM python:3.12

WORKDIR /app

RUN apt-get update
RUN apt-get install zip -y

COPY ./requirements.txt .
RUN pip install -r requirements.txt -t .

COPY . .

RUN zip -r package.zip .
