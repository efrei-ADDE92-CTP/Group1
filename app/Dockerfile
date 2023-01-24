FROM python:3.7.16-slim-bullseye

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

COPY 01-API.py /var/server/app.py

CMD ["python", "/var/server/app.py"]
