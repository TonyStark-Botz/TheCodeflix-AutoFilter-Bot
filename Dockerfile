FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /RX-AUTOFILER2
COPY requirements.txt /RX-AUTOFILER2/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /RX-AUTOFILER2
CMD ["python", "bot.py"]
