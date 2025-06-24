FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/chromium/:${PATH}"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY webscraping.py .

CMD ["python", "-u", "webscraping.py"]
