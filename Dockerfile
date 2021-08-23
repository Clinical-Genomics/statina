FROM python:3.8-slim

LABEL base_image="python:3.8-slim"
LABEL about.home="https://github.com/Clinical-Genomics/statina"
LABEL about.tags="NIPT,statistics,Non Invasive Prenatal Test,python"


ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400
ENV DB_URI="mongodb://localhost:27017/statina-demo"
ENV DB_NAME="statina-demo"
ENV SERVICE_SCOPE="external"

EXPOSE 8000

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install app requirements
RUN pip install -r requirements.txt

# Install app
RUN pip install -e .

CMD gunicorn \
    --workers=$GUNICORN_WORKERS \
    --bind=$GUNICORN_BIND  \
    --threads=$GUNICORN_THREADS \
    --timeout=$GUNICORN_TIMEOUT \
    --proxy-protocol \
    --forwarded-allow-ips="10.0.2.100,127.0.0.1" \
    --log-syslog \
    --access-logfile - \
    --log-level="debug" \
    --worker-class=uvicorn.workers.UvicornWorker \
    statina.main:$SERVICE_SCOPE\_app