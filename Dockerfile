FROM python:3.13-slim

WORKDIR /app

RUN apt update && apt install build-essential -y

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY . ./

ENTRYPOINT ["docker-entrypoint.sh"]
