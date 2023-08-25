FROM andgineer/matplotlib

RUN apk --no-cache --update \
      add build-base zlib-dev \
      cairo-dev cairo cairo-tools \
      jpeg-dev openjpeg-dev tiff-dev \
      freetype-dev lcms2-dev tk-dev tcl-dev

COPY requirements.docker.txt /requirements.docker.txt
COPY requirements.dev.txt /requirements.dev.txt

RUN pip install --no-cache-dir -r requirements.dev.txt \
    && pip install --no-cache-dir -r requirements.docker.txt \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

COPY docker/fonts $HOME/.fonts/

COPY src  /iot_calendar/
COPY tests /tests
COPY pytest.ini /
COPY conftest.py /
COPY test.sh /

EXPOSE 4444

WORKDIR /iot_calendar

CMD ["python3", "iot_calendar.py"]
