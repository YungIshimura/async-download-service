FROM python:3.10.14

RUN apt-get update && \
    apt-get install -y \
    zip \
    build-essential \
    python3-dev \
    libpython3.11-dev \
    gcc \
    libssl-dev \
    libffi-dev \
    make \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080

CMD [ "python", "server.py" ]
