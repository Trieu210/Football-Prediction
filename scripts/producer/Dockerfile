FROM python:3.11-slim
WORKDIR /app

# install deps
COPY producer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy producer code + shared modules
COPY producer/ /app/
COPY apiCallsToCSVFiles/ /app/apiCallsToCSVFiles/
COPY db_pg.py /app/db_pg.py
COPY api_football_live_helper.py /app/api_football_live_helper.py

CMD ["python", "kafka_producer_live_stats.py"]
