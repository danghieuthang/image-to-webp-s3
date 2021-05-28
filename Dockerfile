### Build and install packages
FROM python:3.9 as build-python

RUN apt-get -y update \
  && apt-get install -y gettext \
  # Cleanup apt cache
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install --pre gql

### Final image
FROM python:3.9-slim

RUN apt-get update \
  && apt-get install -y \
  libcairo2 \
  libgdk-pixbuf2.0-0 \
  liblcms2-2 \
  libopenjp2-7 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libssl1.1 \
  libtiff5 \
  libwebp6 \
  libxml2 \
  shared-mime-info \
  mime-support \
  python3-mysqldb \
  vim \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

#change uid and gid of apache to docker user uid/gid
RUN usermod -u 1000 www-data && groupmod -g 1000 www-data

COPY --from=build-python /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/
COPY . /app
WORKDIR /app

EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV DJANGO_STATIC_ROOT=/app/static
RUN mkdir -p  $DJANGO_STATIC_ROOT
RUN STATIC_URL=${DJANGO_STATIC_ROOT} python manage.py collectstatic --noinput

CMD gunicorn core.wsgi --workers=3 --bind :8000
