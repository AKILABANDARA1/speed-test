FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install librespeed-cli
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://github.com/librespeed/speedtest-cli/releases/download/v1.0.11/librespeed-cli_1.0.11_linux_amd64.tar.gz \
    | tar -xz -C /usr/local/bin && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -s /bin/sh -m appuser
USER 10001
EXPOSE 8080
CMD ["python", "app7.py"]
