FROM python:3.8-slim

LABEL base_image="python:3.8-slim"
LABEL about.home="https://github.com/Clinical-Genomics/NIPTool"
LABEL about.tags="NIPT,statistics,Non Invasive Prenatal Test,python"


ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400
ENV DB_URI="mongodb://localhost:27017/nipt-demo"
ENV DB_NAME="nipt-demo"
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
    --forwarded-allow-ips="*" \
    --log-syslog \
    --log-level="debug" \
    --worker-class=uvicorn.workers.UvicornWorker \
    NIPTool.main:$SERVICE_SCOPE\_app