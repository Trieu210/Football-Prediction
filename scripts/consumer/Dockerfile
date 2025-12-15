FROM python:3.11-slim
WORKDIR /app

# install deps
COPY consumer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy consumer code + shared model + db
COPY consumer/ /app/
COPY model/ /app/model/
COPY db_pg.py /app/db_pg.py
COPY data_api_football/ /app/data_api_football/

CMD ["python", "kafka_consumer_predictor.py"]
