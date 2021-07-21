FROM python:3.9

WORKDIR /app
COPY ./page/ /app/page/
COPY ./flask/ /app/flask/
COPY ./requirements/server.txt /app/
RUN pip install --upgrade pip
RUN pip install -r server.txt
EXPOSE $PORT
ENTRYPOINT ["python"]
CMD ["flask/server.py"]