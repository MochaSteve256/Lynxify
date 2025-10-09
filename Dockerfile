# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN pip install py-cord

COPY main.py .
COPY bot_creds.py .
COPY facts.txt .
COPY hottakes.txt .
COPY corporatebsbuzz.txt .
COPY database.db .

CMD ["python", "main.py"]
