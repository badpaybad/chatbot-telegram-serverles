FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
# Cập nhật và cài các dependencies cơ bản
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \ 
    nano \ 
    htop \
    software-properties-common \
    git \
    curl \
    wget \
    postgresql libecpg-dev \
    postgresql-contrib \
    zstd  \
    libpq-dev \
    build-essential \ 
    nodejs \
    npm \ 
    pkg-config

RUN apt-get update && apt-get upgrade -y && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
RUN dpkg -i cloudflared.deb

RUN python3.12 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

RUN source /app/venv/bin/activate

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn pydantic httpx pynacl google-genai telethon matplotlib
# RUN pip install -e .

CMD ["python","program.py","config_dunp"]
