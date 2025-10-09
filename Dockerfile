# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.14-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install dependencies needed to build psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir py-cord sqlalchemy psycopg2-binary

COPY main.py .
COPY bot_creds.py .
COPY facts.txt .
COPY hottakes.txt .
COPY corporatebsbuzz.txt .

CMD ["python", "main.py"]
