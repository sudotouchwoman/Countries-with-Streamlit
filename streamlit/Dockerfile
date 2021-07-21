FROM python:3.9

WORKDIR /app
COPY ./page/ /app/page/
COPY ./streamlit/ /app/streamlit/
COPY ./configs /app/configs/
COPY ./requirements/app.txt /app/
RUN pip install --upgrade pip
RUN pip install -r app.txt
EXPOSE 8051
ENTRYPOINT ["streamlit","run"]
CMD [ "streamlit/build.py" ]