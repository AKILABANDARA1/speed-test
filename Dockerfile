FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install only minimal packages needed (speedtest-cli depends on some binaries)
RUN apt-get update && \
    apt-get install -y openssh-server curl && \
    mkdir /var/run/sshd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Create Choreo-compliant non-root user
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -s /bin/sh -m appuser

# Set password (for local debug — Choreo will likely not expose SSH)
RUN echo 'appuser:password' | chpasswd

USER 10001

EXPOSE 8080 

ENV FLASK_APP=app7.py
ENV FLASK_ENV=production

CMD /usr/sbin/sshd -D & python app7.py
