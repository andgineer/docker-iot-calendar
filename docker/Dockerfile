FROM andgineer/matplotlib

USER root

COPY docker/fonts/* /usr/share/fonts/

RUN apk --no-cache --update add \
      build-base zlib-dev \
      cairo-dev cairo cairo-tools \
      jpeg-dev openjpeg-dev tiff-dev \
      freetype-dev lcms2-dev tk-dev tcl-dev \
    && mkdir -p /static /templates \
    && chown -R leanpython:appgroup /static /templates

USER leanpython

COPY requirements.docker.txt requirements.docker.txt

RUN uv pip install --no-cache-dir -r requirements.docker.txt

COPY src/.  .
COPY static  /static/
COPY templates  /templates/

EXPOSE 4444

CMD ["iot_calendar.py", "--port=4444", "folder=../amazon-dash-private"]
