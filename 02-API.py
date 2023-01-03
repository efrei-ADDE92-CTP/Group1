import requests, os

import pandas as pd

from flask import Flask

from flask import request, jsonify

import joblib

from prometheus_client import start_http_server, Summary,Counter

import random

import time

from multiprocessing.pool import ThreadPool


c = Counter('my_failures', 'Description of counter')



# Create a metric to track time spent and requests made.

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


# Decorate function with metric.


app = Flask(__name__)

with open('knn.pkl', 'rb') as file:

    model = joblib.load(file)


@REQUEST_TIME.time()

@app.route('/predict', methods=['POST'])

def get_predict():

  data = request.get_json(force=True)

  df = pd.DataFrame(data, index=[0])


  for col in model_columns:

    if col not in df.columns:

      df[col] = 0

  c.inc()

  prediction = model.predict(df)

  return jsonify({'prediction': list(prediction)})


if __name__ == '__main__':

    # Start up the server to expose the metrics.

    pool = ThreadPool(1)

    pool.apply_async(start_http_server, (8000, ))

    model_columns = joblib.load('model_columns.pkl')

    app.run(port = 8081,debug=True)

    #curl localhost:8081/predict -H "Content-Type: application/json" -d '{"sepal length (cm)": 5,"sepal width (cm)": 3,"petal length (cm)": 1,"petal width (cm)": 0.2}'