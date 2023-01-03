import requests, os
import pandas as pd
from flask import Flask
from flask import request, jsonify
import joblib

app = Flask(__name__)
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

if __name__ == '__main__':
    model_columns = joblib.load('model_columns.pkl')
    app.run(port = 8081,debug=True)
    #curl localhost:8081/predict -H "Content-Type: application/json" -d '{"sepal length (cm)": 5,"sepal width (cm)": 3,"petal length (cm)": 1,"petal width (cm)": 0.2}' 