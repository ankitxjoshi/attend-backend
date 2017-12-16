FROM python:2.7.14-alpine3.6

ENV FLASK_CONFIG=production
ENV FLASK_APP=run.py
ENV FLASK_DEBUG=1

COPY ./**/* .

RUN pip install -r requirements.txt

EXPOSE 5000:5000

CMD ['flask', 'run']
