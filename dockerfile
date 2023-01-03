FROM python:alpine3.16

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3" , "01-API.py"]
