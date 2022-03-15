FROM python:3.9.5-slim-buster AS app
# template from https://github.com/nickjj/docker-django-example

WORKDIR /app

RUN apt-get update \
  && apt-get install -y build-essential curl libpq-dev nginx --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && mkdir -p /public_collected public \
  && chown python:python -R /public_collected /app

# USER python

COPY --chown=python:python requirements*.txt ./
COPY docker/nginx.conf /etc/nginx/conf.d/nginx.conf
COPY docker/uwsgi.ini /app/uwsgi.ini
#COPY --chown=python:python bin/ ./bin

#RUN chmod 0755 bin/* && bin/pip3-install
RUN pip install -r requirements.txt 

ARG DEBUG="false"
ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

# COPY --chown=python:python --from=webpack /app/public /public
COPY --chown=python:python . .

WORKDIR /app

RUN if [ "${DEBUG}" = "false" ]; then \
  SECRET_KEY=dummyvalue python3 manage.py collectstatic --no-input; \
    else mkdir -p /app/public_collected; fi

RUN chmod +x docker/*
ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]

EXPOSE 8000

# CMD ["gunicorn", "-c", "python:freedb_site.gunicorn", "freedb_site.wsgi"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
