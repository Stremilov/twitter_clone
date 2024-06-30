FROM python:3.8

RUN apt-get update && apt-get install -y python3-dev supervisor nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY src/ /app/
COPY nginx.conf /etc/nginx/ngnix.conf
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY supervisord.ini /etc/supervisor/conf.d/



CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]