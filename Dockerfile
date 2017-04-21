FROM masterandrey/docker-python-base

COPY pip.requirements.txt /pip.requirements.txt
COPY xkcd.otf /

# ADD repositories /etc/apk/repositories # if install numpy with add instead of pip

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && mkdir -p ~/.fonts \
    && cp xkcd.otf ~/.fonts/ \
    # rm -r ~/.cache/matplotlib/* # if some problems with xkcd font
    && apk --no-cache add musl-dev linux-headers gfortran g++ jpeg-dev zlib-dev cairo-dev \
    #  \ # cairo dependencies
    && pip install -r pip.requirements.txt \
    #&& apk add py-matplotlib # better install with pip
    #&& apk add --update py-numpy@community # better install with pip
    # https://hub.docker.com/r/o76923/alpine-numpy-stack/~/dockerfile/
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

COPY src  /iot_calendar/

EXPOSE 4444

WORKDIR /iot_calendar

CMD ["python3", "iot_calendar.py"]
