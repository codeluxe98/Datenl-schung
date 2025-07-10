FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app/app.py
CMD ["flask", "run", "--host=0.0.0.0"]
