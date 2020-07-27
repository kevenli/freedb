FROM python:3.8.1-alpine3.11

RUN apk add libffi-dev \
    openssl-dev gcc libc-dev make libxml2-dev libxslt-dev \
    tzdata jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN cd /app && python setup.py install
RUN pip install uwsgi
WORKDIR /app
ENV TZ /usr/share/zoneinfo/Etc/UTC
RUN python manage.py collectstatic --noinput
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uwsgi", "--ini", "freedb_site/uwsgi.ini"]