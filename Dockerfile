FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8
ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static
COPY . /app
RUN apk add --update --no-cache py3-lxml
RUN pip install -r /app/requirements.txt
