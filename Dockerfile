FROM python:3.9-slim

WORKDIR /app

# Install CA certs to fix SSL
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -s /bin/sh -m appuser
USER 10001

EXPOSE 8080

CMD ["python", "app7.py"]
