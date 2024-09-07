FROM andgineer/matplotlib

RUN apk --no-cache --update \
      add build-base zlib-dev \
      cairo-dev cairo cairo-tools \
      jpeg-dev openjpeg-dev tiff-dev \
      freetype-dev lcms2-dev tk-dev tcl-dev

COPY requirements.docker.txt /requirements.docker.txt

RUN uv pip install --no-cache-dir -r requirements.docker.txt

# At build time $HOME is not defined. And we cannot use ARG - COPY do not substitute it
# As do not want to mess with system defined HOME, thus use _HOME
ENV _HOME /root
COPY docker/fonts/* ${_HOME}/.fonts/

COPY src  /iot_calendar/
COPY static  /static/
COPY templates  /templates/

EXPOSE 4444

WORKDIR /iot_calendar

CMD ["python3", "iot_calendar.py", "--port=4444", "folder=../amazon-dash-private"]
