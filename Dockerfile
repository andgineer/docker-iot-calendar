FROM masterandrey/docker-python-base

COPY pip.requirements.txt /pip.requirements.txt
COPY xkcd.otf /

# ADD repositories /etc/apk/repositories

RUN apk add jpeg-dev zlib-dev cairo-dev \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && mkdir -p ~/.fonts \
    && cp xkcd.otf ~/.fonts/ \
    # rm -r ~/.cache/matplotlib/*
    && apk --no-cache add musl-dev linux-headers gfortran g++ \
    && pip install -r pip.requirements.txt \
    #&& apk del python3-dev libxslt-dev libxml2-dev \
    #&& apk add python3-tk
    #&& apk add py-matplotlib # better install with pip
    #&& apk add --update py-numpy@community # better install with pip
    # https://hub.docker.com/r/o76923/alpine-numpy-stack/~/dockerfile/
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

COPY src  /iot_calendar/

EXPOSE 4444

WORKDIR /iot_calendar

CMD ["python3", "iot_calendar.py"]
