FROM python:3.9-slim

LABEL maintainer="moives.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libjpeg-dev \
        build-essential \
        libpq-dev \
        gcc \
        g++ \
        git \
        cmake \
        && \
    /py/bin/pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu && \
    /py/bin/pip install --no-cache-dir \
        torch-scatter==2.1.1 \
        torch-sparse==0.6.17 \
        torch-cluster==1.6.1 \
        torch-spline-conv==1.2.2 \
        torch-geometric==2.3.1 \
        -f https://data.pyg.org/whl/torch-2.0.1+cpu.html && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    rm -rf /var/lib/apt/lists/* && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol  && \
    chmod -R +x /scripts
ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

CMD ["/scripts/run.sh"]