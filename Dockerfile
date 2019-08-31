FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8
ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static
COPY . /app
COPY ./conf/nginx/nginx.conf /app/nginx.conf
RUN apk add --no-cache py3-lxml
RUN apk add --no-cache mariadb-connector-c-dev
RUN apk add --no-cache --virtual .build-deps build-base 
RUN pip install -r /app/requirements.txt
RUN apk del .build-deps
