FROM andgineer/matplotlib

COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt \
    && rm -rf ~/.pip/cache/ \
    && rm -rf /var/cache/apk/*

COPY src  /iot_calendar/

EXPOSE 4444

WORKDIR /iot_calendar

CMD ["python3", "iot_calendar.py"]
