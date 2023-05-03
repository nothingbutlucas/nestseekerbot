FROM python:3.10

RUN pip install --upgrade pip && mkdir /app


ADD requirements.txt /app
ADD main.py /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python3 /app/main.py
