import requests, os
import logging
import pandas as pd
from flask import Flask
from flask import request, jsonify
import joblib
from prometheus_client import start_http_server, Gauge, Counter 
import random
import time

with open('knn.pkl', 'rb') as file:
    model = joblib.load(file)

app = Flask(__name__)

# a = Counter('a_requests', 'Number of requests served')  
# s = Counter('s_requests', 'Number of sucessful requests')  
# f = Counter('f_requests', 'Number of failed requests')
# g = Gauge('success_rate_requests', 'Rate of success requests')

@app.route('/predict', methods=['POST'])
def get_predict():
    #a.inc()
    data = request.get_json(force=True)
    df = pd.DataFrame(data, index=[0])
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
    prediction = model.predict(df)

    return jsonify({'prediction': list(prediction)})

# @app.after_request
# def log_the_status_code(response):
#     if response.status_code == 200:
#         s.inc()
#     else:
#         f.inc()
#     success_rate = (s._value / (f._value + s._value)) * 100           #.get() removed
#     g.set(success_rate)
#     logging.warning("status as string %s" % response.status)
#     logging.warning("status as integer %s" % response.status_code)
#     return response

if __name__ == '__main__':

    # Start up the server to expose the metrics.
    model_columns = joblib.load('model_columns.pkl')
    
    #start_http_server(5050) 
    app.run(port = 5000)


    #sudo docker build . -t knn:0.0.1
    #sudo docker run --network host -it knn:0.0.1   
    
    #curl localhost:5000/predict -H "Content-Type: application/json" -d '{"sepal length (cm)": 5,"sepal width (cm)": 3,"petal length (cm)": 1,"petal width (cm)": 0.2}'
    #curl localhost:5050/metrics
    