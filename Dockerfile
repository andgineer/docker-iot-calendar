FROM masterandrey/docker-python

COPY server /
WORKDIR /server

EXPOSE 8080

ENTRYPOINT ["python3", "app.py"]
CMD [""]
