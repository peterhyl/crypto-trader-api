FROM python:3.6-alpine
LABEL maintainer="Peter Hyl <peter.hyl.github@gmail.com>"

RUN mkdir /backend
WORKDIR /backend
COPY . /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 pip install --upgrade pip && \
 pip install --no-cache-dir -r requirements.txt
EXPOSE 5001

ENTRYPOINT ["python", "wsgi.py"]