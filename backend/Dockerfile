FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/run.sh

EXPOSE 8000

CMD ["sh", "./run.sh"]

