FROM python:3.12-slim

WORKDIR /app

COPY analytics/python/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONPATH=/app/src

CMD ["sleep", "infinity"]