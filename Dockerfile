# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install build tools and libpq-dev
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && pip install py-cord sqlalchemy psycopg2 \
    && apt-get remove -y build-essential gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install py-cord sqlalchemy psycopg2-binary

COPY main.py .
COPY bot_creds.py .
COPY facts.txt .
COPY hottakes.txt .
COPY corporatebsbuzz.txt .

CMD ["python", "main.py"]
