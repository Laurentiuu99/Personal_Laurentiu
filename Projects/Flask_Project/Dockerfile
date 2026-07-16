FROM python:3.14.6

WORKDIR /kodekloud-twelve-factor-app

COPY requirements.txt /kodekloud-twelve-factor-app/

RUN pip install -r requirements.txt --no-cache-dir

COPY . /kodekloud-twelve-factor-app

CMD python app.py
