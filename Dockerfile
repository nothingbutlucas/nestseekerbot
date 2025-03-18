FROM --platform=linux/arm64/v8 python:3.9.21-bookworm

RUN pip install --upgrade pip && mkdir /app

ADD requirements.txt /app
ADD main.py /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python3 /app/main.py
