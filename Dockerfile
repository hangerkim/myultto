FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8
ENV STATIC_URL /static
ENV STATIC_PATH /app/app/static
RUN rm -rf /app
COPY ./app /app
COPY ./requirements.txt /app/requirements.txt
RUN apk add --update --no-cache py3-lxml
RUN pip install -r /app/requirements.txt
