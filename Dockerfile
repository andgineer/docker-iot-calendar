FROM masterandrey/docker-python-base

COPY pip.requirements.txt /pip.requirements.txt
COPY server/*  /server/

RUN apk add jpeg-dev zlib-dev cairo-dev \
    && pip install -r pip.requirements.txt \
    #&& apk del python3-dev libxslt-dev libxml2-dev \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

EXPOSE 4444

WORKDIR /server

CMD ["python3", "app.py"]
