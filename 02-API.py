import requests, os

import pandas as pd

from flask import Flask

from flask import request, jsonify

import joblib

from werkzeug.middleware.dispatcher import DispatcherMiddleware

from prometheus_client import start_http_server, Summary,Counter, make_wsgi_app

from prometheus_flask_exporter import PrometheusMetrics

import random

import time

# Decorate function with metric.


app = Flask(__name__)

metrics = PrometheusMetrics(app)

with open('knn.pkl', 'rb') as file:

    model = joblib.load(file)



@app.route('/predict', methods=['POST'])
def get_predict():

  data = request.get_json(force=True)

  df = pd.DataFrame(data, index=[0])


  for col in model_columns:

    if col not in df.columns:

      df[col] = 0

  prediction = model.predict(df)

  return jsonify({'prediction': list(prediction)})

response_data, content_type = metrics.generate_metrics()



if __name__ == '__main__':

    # Start up the server to expose the metrics.

    model_columns = joblib.load('model_columns.pkl')
    
    app.run(debug=False)

    #curl localhost:5000/predict -H "Content-Type: application/json" -d '{"sepal length (cm)": 5,"sepal width (cm)": 3,"petal length (cm)": 1,"petal width (cm)": 0.2}'